# 03 - Tool Catalog

> **Generated file.** Source of truth: [`specs/tool-catalog.yaml`](../specs/tool-catalog.yaml).
> Edit the YAML and run `python scripts/render_tool_catalog.py`. Detailed contracts for the
> Phase 1 tools are in [04-tool-specifications.md](04-tool-specifications.md).

## How to read this catalog

| Column | Meaning |
|---|---|
| **ID** | Stable id used in stories, tests and traces |
| **Tool** | MCP tool name the agent calls |
| **What it answers** | The question the tool answers, in plain words |
| **How it gets the answer** | Source system and API / SQL |
| **REST endpoint** | Same handler exposed through the Access Diagnostics API |
| **Ph** | Delivery phase: 1 MVP, 2 depth + monitoring, 3 Databricks / Starburst / storage, 4 onboarding |
| **Type** | `read`, `derived` (computed from other tools), `write` (needs confirmation in chat) |
| **Scope** | Minimum requester scope to run the tool for *another* user: `self` < `support` < `steward` < `platform` |
| **Fresh** | `live`, `lagged(max lag)` or `cached(ttl)`. Lagged tools always return `data_as_of`. |

A **(v)** after the tool name means an upstream API or SQL detail must be confirmed against the
deployed product version during spike CAA-003 before the tool is built.

## Your seven starting tools, mapped

| You asked for | Tool(s) |
|---|---|
| 1. User attributes and groups from the Immuta API | `immuta_get_user_entitlements` (IM-02), with `immuta_get_user` (IM-01) |
| 2. Tables / data products the user has access to, from telemetry | `telemetry_get_user_access` (DP-04) |
| 3. Roles the user has on Snowflake | `snowflake_get_user_roles` (SF-02) |
| 4. Tables the user has access to in Snowflake | `snowflake_list_accessible_tables` (SF-04), `snowflake_check_object_privileges` (SF-03) |
| 5. Last 10 failed queries in the last 5 days | `snowflake_get_failed_queries` (SF-05) |
| 6. Row-level security: which accounts the user can see | `entitlement_get_row_visibility` (EN-01), backed by `immuta_get_user_policy_info` (IM-07) |
| 7. What PI access the user has | `entitlement_get_pi_access` (EN-02), backed by IM-07, IM-11 and SF-07 |

## Totals

| Phase | Tools |
|---|---|
| 1 | 32 |
| 2 | 27 |
| 3 | 18 |
| 4 | 5 |
| **All** | **82** |


## A. Identity and directory (Active Directory / Entra ID)

| ID | Tool | What it answers | How it gets the answer | REST endpoint | Ph | Type | Scope | Fresh |
|---|---|---|---|---|---|---|---|---|
| ID-01 | `identity_resolve_user` | Map one person to their identity in every system (Entra ID, Immuta, Snowflake, Databricks, Starburst) and flag mismatches. | Entra lookup by UPN/mail/sAMAccountName, then Immuta GET /bim/user?userid=, then Snowflake USERS by login_name/email. Cached 15 min. | `GET /v1/users/{user}/identity` | 1 | derived | support | cached(15m) |
| ID-02 | `idp_get_user` | Directory account status - enabled or disabled, UPN, mail, department, manager, account type, on-prem sync status. | Microsoft Graph GET /users/{id}?$select=accountEnabled,userPrincipalName,mail,onPremisesSamAccountName,department,onPremisesSyncEnabled,onPremisesLastSyncDateTime (+ /manager) | `GET /v1/users/{user}/directory` | 1 | read | support | live |
| ID-03 | `idp_get_user_groups` | All AD/Entra groups the user belongs to, including nested membership, filtered to data-mesh group prefixes. | Graph GET /users/{id}/transitiveMemberOf/microsoft.graph.group (paged, ConsistencyLevel: eventual). Filter by configured prefixes, e.g. DM-*, SNOW-*. | `GET /v1/users/{user}/directory/groups` | 1 | read | support | live |
| ID-04 | `idp_check_group_membership` | Yes/no answer - is the user a (transitive) member of the named groups. | Graph POST /users/{id}/checkMemberGroups with up to 20 group ids per call | `POST /v1/users/{user}/directory/groups:check` | 1 | read | support | live |
| ID-05 | `idp_get_group_details` | Group description, owners, membership type (assigned or dynamic rule) and how to request membership. | Graph GET /groups/{id}?$select=displayName,description,groupTypes,membershipRule + /owners. Request route from config/access-request-routes.yaml. | `GET /v1/directory/groups/{group}` | 2 | read | self | live |
| ID-06 | `idp_get_group_change_log` (v) | When the user was added to or removed from a group, and by whom - used for 'it worked yesterday' and propagation-lag cases. | Graph GET /auditLogs/directoryAudits filtered on category GroupManagement and target user (requires AuditLog.Read.All; retention depends on licence) | `GET /v1/users/{user}/directory/group-changes` | 2 | read | support | live |
| ID-07 | `idp_get_user_attributes` | Directory extension attributes that feed ABAC (for example region, entity, clearance) at the source, before Immuta maps them. | Graph GET /users/{id}?$select=<configured extension attributes>. Attribute list in config/attribute-map.yaml. | `GET /v1/users/{user}/directory/attributes` | 2 | read | support | live |

## B. Immuta

| ID | Tool | What it answers | How it gets the answer | REST endpoint | Ph | Type | Scope | Fresh |
|---|---|---|---|---|---|---|---|---|
| IM-01 | `immuta_get_user` | Immuta user record - exists or not, disabled flag, IAM source, external user id mappings (Snowflake, Databricks, Trino user names). | GET /bim/user?userid={upn} to find the numeric id, then GET /bim/iam/{iamid}/user/{id} (USER_ADMIN or AUDIT permission) | `GET /v1/users/{user}/immuta` | 1 | read | support | live |
| IM-02 | `immuta_get_user_entitlements` | Groups and attributes (authorizations) Immuta holds for the user, with where each came from - IAM sync, set in Immuta, or inherited from a group. | GET /bim/iam/{iamid}/user/{id} -> authorizations, bimAuthorizations, iamAuthorizations, groups; GET /bim/iam/{iamid}/user/{userid}/groups; group-level attributes from GET /bim/group/{groupId} | `GET /v1/users/{user}/immuta/entitlements` | 1 | read | support | live |
| IM-03 | `immuta_find_data_source` | Resolve a platform table name or data product name to the Immuta data source(s) that govern it. | GET /dataSource?searchText=&schema=&size= ; GET /dataSource/sqlTableName/{shortName}; match on connection + remote schema/table | `GET /v1/immuta/data-sources?table={table}&platform={platform}` | 1 | read | self | cached(10m) |
| IM-04 | `immuta_get_data_source` | Data source health and governance summary - enabled, health status, owners, applied global policies, tags, last schema detection. | GET /dataSource/{dataSourceId} (status, statusInfo, subscriptionPolicy, globalPolicies, deleted) + GET /dataSource/{id}/contacts | `GET /v1/immuta/data-sources/{data_source_id}` | 1 | read | self | live |
| IM-05 | `immuta_get_subscription_status` | Is this user subscribed to this data source - subscribed, pending, denied, not subscribed, expired - and how they got it (policy or manual). | GET /dataSource/{dataSourceId}/access?searchText={userid}&expandGroups=true -> state, approved, approvals, subscriptionId | `GET /v1/users/{user}/immuta/data-sources/{data_source_id}/subscription` | 1 | read | support | live |
| IM-06 | `immuta_get_subscription_policy` (v) | The subscription policy on a data source expressed as required groups and attributes, in machine-readable and plain-English form. | subscriptionPolicy object from GET /dataSource/{id}; global policy detail from the v1 policy API. Normalise to the condition tree in docs/06. | `GET /v1/immuta/data-sources/{data_source_id}/subscription-policy` | 1 | read | self | cached(10m) |
| IM-07 | `immuta_get_user_policy_info` | What Immuta will enforce for this user on this data source - row filters, masked columns and visibilities. The primary source for RLS and PI answers. | GET /dataSource/{dataSourceId}/users/{profileId}/policyInfo (FETCH_POLICY_INFO) -> visibilities, visibilityRuleApplies, masked, additionalFilters; optional /visibilityReport (GOVERNANCE) | `GET /v1/users/{user}/immuta/data-sources/{data_source_id}/policy-info` | 1 | read | support | live |
| IM-08 | `immuta_list_user_data_sources` (v) | Every data source the user is subscribed to in Immuta. | Option A: Immuta audit/UAM export in S3 queried with Athena. Option B: per-user Snowflake role grants (SF-04) joined to IM-03. Option C: page GET /dataSource and filter on /access. Choose in spike CAA-003. | `GET /v1/users/{user}/immuta/data-sources` | 2 | read | support | lagged(1h) |
| IM-09 | `immuta_get_data_policies` (v) | Data policies (masking and row-level rules) applied to a data source, with their exception conditions. | v1 policy API - policy handler for the data source plus global policy definitions. Normalise rules and exceptions to the condition tree in docs/06. | `GET /v1/immuta/data-sources/{data_source_id}/data-policies` | 2 | read | steward | cached(10m) |
| IM-10 | `immuta_get_data_source_activity` | Recent policy and subscription activity on a data source - who changed what and when. | GET /dataSource/{dataSourceId}/activities?size=&offset= | `GET /v1/immuta/data-sources/{data_source_id}/activity` | 2 | read | steward | live |
| IM-11 | `immuta_get_data_source_tags` (v) | Column-level tags on a data source, used to identify PI / sensitive columns. | GET /dataSource/{dataSourceId}/tags plus the data dictionary for column tags. PI tag list in config/pi-classification.yaml. | `GET /v1/immuta/data-sources/{data_source_id}/tags` | 1 | read | self | cached(10m) |
| IM-12 | `immuta_get_integration_status` | Health of each Immuta integration (Snowflake, Databricks Unity Catalog, Starburst) so platform-wide faults are ruled out first. | GET /integrations and GET /integrations/{id}/status (status, validationResults) | `GET /v1/immuta/integrations` | 1 | read | self | cached(2m) |
| IM-13 | `immuta_get_access_requests` (v) | Open or recent access requests the user has raised in Immuta and who must approve them. | GET /dataSource/{dataSourceId}/tasks (and Immuta Request app API/webhooks if the Request app is in use) | `GET /v1/users/{user}/immuta/access-requests` | 2 | read | support | live |
| IM-14 | `immuta_get_audit_events` | Immuta audit events for a user or data source - subscription granted or revoked, policy applied, query denied. | Immuta Universal Audit Model export to S3, queried through Athena (table caa_audit.immuta_uam). Avoids load on the Immuta API. | `GET /v1/immuta/audit-events` | 2 | read | support | lagged(1h) |
| IM-15 | `immuta_get_user_projects` (v) | Immuta projects and purposes the user belongs to, for purpose-based access rules. | v1 project API filtered by member | `GET /v1/users/{user}/immuta/projects` | 3 | read | support | live |
| IM-16 | `immuta_explain_subscription_decision` | Deterministic evaluation of the subscription policy against the user's entitlements - which conditions pass, which fail, and exactly what is missing. | Pure function in caa_core.policy_eval over IM-02 + IM-06 output. No LLM involved. | `GET /v1/users/{user}/immuta/data-sources/{data_source_id}/subscription-decision` | 1 | derived | support | live |

## C. Snowflake

| ID | Tool | What it answers | How it gets the answer | REST endpoint | Ph | Type | Scope | Fresh |
|---|---|---|---|---|---|---|---|---|
| SF-01 | `snowflake_get_user` | Snowflake user status - exists, disabled, locked, expired, default role, default warehouse, default secondary roles, last successful login. | SNOWFLAKE.ACCOUNT_USAGE.USERS (sql/snowflake/get_user.sql) | `GET /v1/users/{user}/snowflake` | 1 | read | support | lagged(2h) |
| SF-02 | `snowflake_get_user_roles` | Roles granted to the user directly and through the role hierarchy, flagging the Immuta-managed per-user role. | Recursive CTE over ACCOUNT_USAGE.GRANTS_TO_USERS and GRANTS_TO_ROLES (sql/snowflake/get_user_roles.sql). Immuta role = <PREFIX>_USER_<username>. | `GET /v1/users/{user}/snowflake/roles` | 1 | read | support | lagged(2h) |
| SF-03 | `snowflake_check_object_privileges` | Full privilege chain for a table - USAGE on database, USAGE on schema, SELECT on table - and which of the user's roles supplies each link. | GRANTS_TO_ROLES joined to the effective role set from SF-02 (sql/snowflake/check_object_privileges.sql) | `GET /v1/users/{user}/snowflake/tables/{table}/privileges` | 1 | read | support | lagged(2h) |
| SF-04 | `snowflake_list_accessible_tables` | Tables and views the user can SELECT in Snowflake through any role, limited to data-mesh databases. | GRANTS_TO_ROLES for the effective role set, privilege SELECT, filtered by config/data-mesh-scope.yaml (sql/snowflake/list_accessible_tables.sql) | `GET /v1/users/{user}/snowflake/tables` | 1 | read | support | lagged(2h) |
| SF-05 | `snowflake_get_failed_queries` | The user's most recent failed queries (default last 10 in last 5 days) with error code, message, role, secondary roles and warehouse. | ACCOUNT_USAGE.QUERY_HISTORY where execution_status is FAIL/INCIDENT (sql/snowflake/get_failed_queries.sql). Query text truncated and literal-redacted. | `GET /v1/users/{user}/snowflake/failed-queries?days=5&limit=10` | 1 | read | support | lagged(45m) |
| SF-06 | `snowflake_get_query_details` | Details of one query by id - status, error, session role context, objects referenced - when the user pastes a query id. | QUERY_HISTORY by query_id, plus ACCESS_HISTORY for objects and policies referenced (sql/snowflake/get_query_details.sql) | `GET /v1/snowflake/queries/{query_id}` | 1 | read | support | lagged(45m-3h) |
| SF-07 | `snowflake_get_table_policies` | Row access and masking policies actually attached to the table in Snowflake, to confirm Immuta's policies are enforced on the platform. | ACCOUNT_USAGE.POLICY_REFERENCES by table (sql/snowflake/get_table_policies.sql) | `GET /v1/snowflake/tables/{table}/policies` | 1 | read | support | lagged(2h) |
| SF-08 | `snowflake_get_table_status` | Does the table exist, what type is it (Iceberg, external, view), who owns it, and has it been dropped or recreated recently. | ACCOUNT_USAGE.TABLES including deleted rows, most recent 5 versions (sql/snowflake/get_table_status.sql) | `GET /v1/snowflake/tables/{table}` | 1 | read | self | lagged(2h) |
| SF-09 | `snowflake_get_login_history` | Recent login attempts and failures with error code, client type and authentication factor - for 'cannot connect' cases. | ACCOUNT_USAGE.LOGIN_HISTORY (sql/snowflake/get_login_history.sql). Client IP returned only to platform scope. | `GET /v1/users/{user}/snowflake/logins` | 2 | read | support | lagged(2h) |
| SF-10 | `snowflake_get_access_history` | When the user last read a table successfully, and with which role - proves 'it used to work' and dates the regression. | ACCOUNT_USAGE.ACCESS_HISTORY flattened on base_objects_accessed (sql/snowflake/get_access_history.sql) | `GET /v1/users/{user}/snowflake/tables/{table}/access-history` | 2 | read | support | lagged(3h) |
| SF-11 | `snowflake_get_iceberg_table_health` (v) | For Iceberg tables - catalog integration, external volume reachability, auto-refresh state and last refreshed snapshot. | SHOW ICEBERG TABLES, SYSTEM$AUTO_REFRESH_STATUS, SYSTEM$VERIFY_EXTERNAL_VOLUME, SYSTEM$GET_ICEBERG_TABLE_INFORMATION | `GET /v1/snowflake/tables/{table}/iceberg-health` | 2 | read | support | live |
| SF-12 | `snowflake_get_warehouse_access` | Warehouses the user can use, their state, and whether a resource monitor has suspended them. | GRANTS_TO_ROLES (granted_on WAREHOUSE, privilege USAGE/OPERATE) for the effective role set + SHOW WAREHOUSES | `GET /v1/users/{user}/snowflake/warehouses` | 2 | read | support | lagged(2h) |
| SF-13 | `snowflake_get_grant_changes` | Grants and revokes affecting the user or table in a time window - what changed between 'worked' and 'broken'. | GRANTS_TO_USERS / GRANTS_TO_ROLES rows with created_on or deleted_on in the window (sql/snowflake/get_grant_changes.sql) | `GET /v1/users/{user}/snowflake/grant-changes` | 2 | read | support | lagged(2h) |
| SF-14 | `snowflake_get_auth_policies` (v) | Network and authentication policies that apply to the user, for IP-block and MFA/SSO failures. | ACCOUNT_USAGE.POLICY_REFERENCES (user-level) + NETWORK_POLICIES; SHOW PARAMETERS for account defaults | `GET /v1/users/{user}/snowflake/auth-policies` | 3 | read | platform | lagged(2h) |
| SF-15 | `snowflake_probe_as_user` | OPTIONAL ground-truth probe - run a metadata-only count as the user through their own OAuth token, to confirm effective access. Off by default. | Snowflake External OAuth on-behalf-of token from AgentCore Identity. Runs SELECT COUNT(*) only. See ADR-005. | `POST /v1/users/{user}/snowflake/tables/{table}:probe` | 3 | read | self | live |

## D. Entitlements (derived, cross-system)

| ID | Tool | What it answers | How it gets the answer | REST endpoint | Ph | Type | Scope | Fresh |
|---|---|---|---|---|---|---|---|---|
| EN-01 | `entitlement_get_row_visibility` | Row-level security answer - which accounts (or other row-scope values) the user can see on a table, and which attribute or mapping grants each. | IM-07 row filters + IM-02 attribute values; if the policy uses a lookup table, read the entitlement mapping table (config/rls-models.yaml). Never reads business rows. | `GET /v1/users/{user}/tables/{table}/row-visibility` | 1 | derived | support | live |
| EN-02 | `entitlement_get_pi_access` | PI access answer - which PI columns are clear or masked for the user on a table (or across their tables), and what would unmask them. | IM-11 column tags + IM-07 masked columns + SF-07 attached masking policies; exception conditions from IM-09 | `GET /v1/users/{user}/pi-access?table={table}` | 1 | derived | support | live |
| EN-03 | `entitlement_get_access_summary` | One-call 360 view of a user - identity status in each system, groups, attributes, roles, subscribed data products, PI and RLS headline. | Fan-out to ID-01, ID-03, IM-02, SF-01, SF-02, DP-04 in parallel; assemble; cache 5 min | `GET /v1/users/{user}/access-summary` | 1 | derived | support | cached(5m) |
| EN-04 | `entitlement_compare_users` | Side-by-side difference between two users for one table - groups, attributes, roles, subscription - for 'my colleague can see it and I cannot'. | EN-03 for both users + DX-01 for both; set difference. Requires support scope, or both users' consent. | `POST /v1/entitlements:compare` | 2 | derived | support | live |
| EN-05 | `entitlement_diff_over_time` | What changed in a user's entitlements between two dates, from stored daily access snapshots. | Daily EN-03 snapshots written to S3 by the monitoring pipeline, queried with Athena | `GET /v1/users/{user}/access-summary:diff?from=&to=` | 3 | derived | support | lagged(24h) |

## E. Data product catalog

| ID | Tool | What it answers | How it gets the answer | REST endpoint | Ph | Type | Scope | Fresh |
|---|---|---|---|---|---|---|---|---|
| DP-01 | `catalog_search_data_products` | Find a data product or table by name, keyword or owner in the data mesh catalog. | Data mesh catalog / registration service API (adapter interface CatalogPort; implementation depends on the existing catalog) | `GET /v1/data-products?query=` | 1 | read | self | cached(10m) |
| DP-02 | `catalog_get_data_product` | Data product detail and access contract - owner, tables, storage format, platforms it is registered on, required AD group and attributes. | Catalog API + config/access-contracts overrides | `GET /v1/data-products/{data_product_id}` | 1 | read | self | cached(10m) |
| DP-03 | `catalog_get_registration_status` | Whether a producer table is registered on each consumer platform and in Immuta, and the state of the last registration run. | Registration pipeline status store (Step Functions execution history / DynamoDB status table) | `GET /v1/data-products/{data_product_id}/registration` | 2 | read | self | live |

## E. Telemetry

| ID | Tool | What it answers | How it gets the answer | REST endpoint | Ph | Type | Scope | Fresh |
|---|---|---|---|---|---|---|---|---|
| DP-04 | `telemetry_get_user_access` | Tables and data products the user has access to according to platform telemetry - the fast inventory answer to 'what can I access'. | Telemetry store query (TelemetryPort adapter - Snowflake table or Athena, per the existing telemetry design) | `GET /v1/users/{user}/data-products` | 1 | read | support | lagged(per telemetry SLA) |
| DP-05 | `telemetry_get_user_usage` | What the user actually queried recently - tables, counts, last used - to separate 'has access' from 'uses'. | Telemetry store; falls back to SF-10 / DB-04 | `GET /v1/users/{user}/usage` | 2 | read | support | lagged(per telemetry SLA) |
| DP-06 | `telemetry_get_data_product_health` | Freshness and pipeline status of a data product, so 'no data' is not misdiagnosed as an access problem. | Producer pipeline telemetry / data quality store | `GET /v1/data-products/{data_product_id}/health` | 2 | read | self | lagged(per telemetry SLA) |

## F. Producer storage (AWS)

| ID | Tool | What it answers | How it gets the answer | REST endpoint | Ph | Type | Scope | Fresh |
|---|---|---|---|---|---|---|---|---|
| AW-01 | `aws_get_glue_table` | Glue Data Catalog entry for the producer table - exists, table type, location, last update. | glue:GetTable through a cross-account read role in the producer account | `GET /v1/aws/glue/tables/{database}/{table}` | 3 | read | platform | live |
| AW-02 | `aws_get_iceberg_metadata_status` | Current Iceberg snapshot of the producer table - snapshot id, commit time, metadata file - to compare with what the consumer platform sees. | Read Glue metadata_location, then the metadata JSON from S3 (PyIceberg, read-only) | `GET /v1/aws/iceberg/tables/{database}/{table}` | 3 | read | platform | live |
| AW-03 | `aws_check_storage_access_path` | Can the consumer platform's storage role still read the producer bucket - IAM, bucket policy and KMS key policy evaluation. | iam:SimulatePrincipalPolicy for s3:GetObject / kms:Decrypt on the table prefix; bucket and key policy inspection | `POST /v1/aws/storage-access:check` | 3 | read | platform | live |

## G. Databricks

| ID | Tool | What it answers | How it gets the answer | REST endpoint | Ph | Type | Scope | Fresh |
|---|---|---|---|---|---|---|---|---|
| DB-01 | `databricks_get_user` | Databricks account user - active or not, groups, workspace assignment. | Account SCIM API /api/2.1/accounts/{account_id}/scim/v2/Users?filter=userName eq ... | `GET /v1/users/{user}/databricks` | 3 | read | support | live |
| DB-02 | `databricks_get_effective_permissions` | Effective Unity Catalog privileges for the user on a table, including those inherited from schema and catalog. | GET /api/2.1/unity-catalog/effective-permissions/table/{full_name}?principal={user} (paginated) | `GET /v1/users/{user}/databricks/tables/{table}/privileges` | 3 | read | support | live |
| DB-03 | `databricks_list_accessible_tables` | Unity Catalog tables the user can read. | system.information_schema.table_privileges for the user and their groups, via a SQL warehouse | `GET /v1/users/{user}/databricks/tables` | 3 | read | support | live |
| DB-04 | `databricks_get_failed_queries` (v) | The user's recent failed queries on SQL warehouses and serverless compute. | system.query.history where execution_status = FAILED. Query text is masked by default from 2026-08 unless the service principal is in databricks_pii_access. | `GET /v1/users/{user}/databricks/failed-queries` | 3 | read | support | lagged(minutes-hours) |
| DB-05 | `databricks_get_table_policies` | Row filters and column masks attached to a Unity Catalog table. | Unity Catalog GET /api/2.1/unity-catalog/tables/{full_name} (row_filter, columns[].mask) or information_schema.row_filters / column_masks | `GET /v1/databricks/tables/{table}/policies` | 3 | read | support | live |
| DB-06 | `databricks_get_table_status` | Table existence, type (managed, external, foreign), storage location, and catalog-to-workspace binding. | Unity Catalog tables API + workspace bindings API | `GET /v1/databricks/tables/{table}` | 3 | read | self | live |
| DB-07 | `databricks_get_audit_events` | Unity Catalog audit events for permission denials and grant changes affecting the user. | system.access.audit filtered on user identity and action names | `GET /v1/users/{user}/databricks/audit-events` | 3 | read | support | lagged(minutes-hours) |

## H. Starburst

| ID | Tool | What it answers | How it gets the answer | REST endpoint | Ph | Type | Scope | Fresh |
|---|---|---|---|---|---|---|---|---|
| SB-01 | `starburst_get_user_roles` (v) | Roles and groups the user holds in Starburst. | Starburst built-in access control REST API, or the group provider configuration | `GET /v1/users/{user}/starburst/roles` | 3 | read | support | live |
| SB-02 | `starburst_check_table_access` | Whether the user should be able to read a Starburst table - Immuta decision plus catalog visibility. | Immuta is the system access control via the Immuta Trino plugin, so IM-05 + IM-07 for the Starburst data source decide; plus SB-04 | `GET /v1/users/{user}/starburst/tables/{table}/access` | 3 | derived | support | live |
| SB-03 | `starburst_get_failed_queries` (v) | The user's recent failed Starburst queries with error type and message. | Starburst query history (Insights / query logger backend database); system.runtime.queries only covers recent in-memory history | `GET /v1/users/{user}/starburst/failed-queries` | 3 | read | support | lagged(minutes) |
| SB-04 | `starburst_get_table_status` | Whether the catalog, schema and table are visible in Starburst and what connector serves them. | information_schema.tables in the target catalog + SHOW CATALOGS, through a service account | `GET /v1/starburst/tables/{table}` | 3 | read | self | live |

## I. Diagnosis (deterministic composites)

| ID | Tool | What it answers | How it gets the answer | REST endpoint | Ph | Type | Scope | Fresh |
|---|---|---|---|---|---|---|---|---|
| DX-01 | `diagnose_table_access` | Runs the whole access chain for one user and one table and returns expected-versus-actual access, root cause codes and next actions. | caa_core.diagnosis engine: layers L0-L5 in docs/06, calling the tools above in parallel. Deterministic; the LLM explains the result, it does not compute it. | `POST /v1/diagnoses/table-access` | 1 | derived | support | live |
| DX-02 | `diagnose_failed_query` | Classifies a failed query (access, session context, SQL error, compute, data availability) and, if access-related, runs DX-01 for the tables involved. | Error-code map config/error-catalog.yaml + SF-06 + sqlglot table extraction + DX-01 | `POST /v1/diagnoses/failed-query` | 1 | derived | support | lagged(45m) |
| DX-03 | `diagnose_row_visibility` | Explains why a user sees no rows or fewer rows than expected - expected scope versus granted scope. | EN-01 + expected value(s) supplied by the user + ID-06/SF-13 for recent changes | `POST /v1/diagnoses/row-visibility` | 2 | derived | support | live |
| DX-04 | `diagnose_masked_columns` | Explains why specific columns are masked or NULL for a user and what entitlement would unmask them. | EN-02 scoped to the named columns + IM-09 exceptions | `POST /v1/diagnoses/masked-columns` | 2 | derived | support | live |
| DX-05 | `diagnose_login_failure` | Explains why a user cannot connect - disabled account, locked, network policy, expired credential, SSO or key-pair problem. | ID-02 + SF-01 + SF-09 (+ SF-14) against config/error-catalog.yaml | `POST /v1/diagnoses/login-failure` | 2 | derived | support | lagged(2h) |

## J. Proactive monitoring

| ID | Tool | What it answers | How it gets the answer | REST endpoint | Ph | Type | Scope | Fresh |
|---|---|---|---|---|---|---|---|---|
| MN-01 | `monitor_get_platform_status` | Current known incidents and degradations across Immuta, Snowflake, Databricks, Starburst and directory sync - always checked first. | DynamoDB table caa-findings (open findings of severity major+) + vendor status feeds where available | `GET /v1/platform-status` | 2 | read | self | cached(1m) |
| MN-02 | `monitor_get_findings` | Findings from the scheduled checks - entitlement drift, sync lag, stale Iceberg refresh, failure spikes - for a user, table or data product. | DynamoDB caa-findings queried by GSI on subject / object | `GET /v1/findings` | 2 | read | support | live |

## K. Workflow and knowledge

| ID | Tool | What it answers | How it gets the answer | REST endpoint | Ph | Type | Scope | Fresh |
|---|---|---|---|---|---|---|---|---|
| WF-01 | `kb_search` | Search runbooks, access guides, FAQs and platform documentation. | Amazon Bedrock Knowledge Bases Retrieve API over the S3 docs corpus | `GET /v1/kb/search?query=` | 1 | read | self | lagged(sync schedule) |
| WF-02 | `kb_get_error_reference` | Curated meaning, likely causes and standard fix for a platform error code or message pattern. | Lookup in config/error-catalog.yaml (versioned in git) | `GET /v1/kb/errors/{platform}/{code}` | 1 | read | self | live |
| WF-03 | `itsm_search_tickets` | The user's open or recent access requests and incidents in the ITSM tool, to avoid duplicates and to check approval status. | ITSM REST API (ServiceNow Table API or Jira Service Management) through the ItsmPort adapter | `GET /v1/users/{user}/tickets` | 2 | read | support | live |
| WF-04 | `itsm_create_ticket` | Raise an incident or access request pre-filled with the diagnosis and evidence. Requires explicit user confirmation in chat. | ITSM REST API create; idempotency key = conversation id + diagnosis id | `POST /v1/tickets` | 2 | write | self | live |
| WF-05 | `iam_get_access_request_status` | Status of an AD group membership request in the identity governance tool - submitted, awaiting approver, provisioned. | Identity governance API (for example SailPoint or Saviynt) through the IgaPort adapter | `GET /v1/users/{user}/group-requests` | 2 | read | support | live |
| WF-06 | `notify_platform_team` | Send a structured escalation with the evidence pack to the owning platform team's channel. Requires confirmation. | SNS topic per team -> Teams/Slack webhook | `POST /v1/escalations` | 2 | write | support | live |
| WF-07 | `report_security_finding` | Silently file an over-entitlement finding (actual access exceeds expected access) to the governance queue. Called by the engine, not offered to end users. | DynamoDB caa-findings + SNS governance topic | `POST /v1/findings` | 2 | write | platform | live |

## L. Consumer onboarding

| ID | Tool | What it answers | How it gets the answer | REST endpoint | Ph | Type | Scope | Fresh |
|---|---|---|---|---|---|---|---|---|
| OB-01 | `onboarding_get_prerequisites` | Everything a new consumer needs for a data product on a chosen platform - accounts, AD groups, attributes, training, network - as an ordered checklist. | DP-02 access contract + platform prerequisite templates in config/onboarding/ | `GET /v1/onboarding/prerequisites?data_product_id=&platform=` | 4 | derived | self | cached(10m) |
| OB-02 | `onboarding_get_checklist_status` | Which prerequisites this user has already completed and which are outstanding, checked live against every system. | OB-01 steps each mapped to a verifying tool (ID-04, IM-05, SF-01, SF-03 ...) | `GET /v1/users/{user}/onboarding/status?data_product_id=&platform=` | 4 | derived | self | live |
| OB-03 | `onboarding_generate_sample_code` | Working starter code to connect and query a data product in the consumer's language and platform, using the organisation's approved connection pattern. | Reviewed templates in templates/sample-code/{platform}/{language} rendered with table and connection parameters. The LLM may adapt but not invent connection patterns. | `POST /v1/onboarding/sample-code` | 4 | derived | self | live |
| OB-04 | `onboarding_get_connection_profile` | Connection details for a platform - account URL, recommended warehouse or compute, role conventions, driver versions, PrivateLink endpoint. | config/onboarding/connection-profiles.yaml per environment | `GET /v1/onboarding/connection-profiles/{platform}` | 4 | read | self | live |
| OB-05 | `onboarding_start_access_request` | Submit the access requests needed for a data product (AD group, Immuta subscription) on the user's behalf. Requires confirmation. | IgaPort / ItsmPort create + Immuta POST /dataSource/subscribe where the policy allows requests | `POST /v1/onboarding/access-requests` | 4 | write | self | live |

