# 04 - Tool Specifications

How every tool behaves, and the detailed build notes for the 32 Phase 1 tools. The list of all tools is in [03-tool-catalog.md](03-tool-catalog.md); the machine-readable source is [`specs/tool-catalog.yaml`](../specs/tool-catalog.yaml); the REST contract is [`api/openapi.yaml`](../api/openapi.yaml).

> **Verification status.** Upstream API paths and SQL in this document were checked against public vendor documentation in November 2026, but nothing here has been run against your tenants. Items marked **VERIFY** must be confirmed in spike CAA-003 before the tool is built.

## 1. Conventions

| Topic | Rule |
|---|---|
| Naming | `<domain>_<verb>_<noun>`, snake_case. Verbs: `get`, `list`, `find`, `check`, `search`, `explain`, `diagnose`, `create`. |
| Subject | Parameter `user` is the person being diagnosed. Accepts UPN, email, sAMAccountName or a platform login. Resolved through `identity_resolve_user`. The literal `self` means the requester. |
| Requester | Never a parameter. Injected by the Gateway from the validated JWT into the invocation context (`requester.upn`, `requester.scopes`). |
| Table names | Fully qualified. Parsed by `caa_core.identifiers.parse_table(platform, name)`, which normalises case per platform and rejects anything that is not an identifier. |
| Read-only | `type: read` and `derived` tools must not change any system. `type: write` tools require `confirmation_token` issued after the user confirms in chat (section 5). |
| Idempotent | All read tools are safe to retry. |
| Size | A tool result is at most 16 KB of JSON. Larger payloads are written to S3 and returned as `evidence[].ref` with a summary. Lists are capped by `limit` and return `total` and `truncated`. |
| Time | ISO 8601 UTC everywhere. |
| Descriptions | The MCP `description` of each tool states what it answers, when to use it, when *not* to use it, and its freshness. The model selects tools from descriptions, so they are part of the contract. |

## 2. Standard response envelope

Every tool returns this shape. The agent prompt relies on `status`, `freshness` and `warnings`.

```json
{
  "tool": "snowflake_get_user_roles",
  "tool_version": "1.0.0",
  "status": "ok",
  "subject": { "user": "asha.rao@example.com", "canonical_user_id": "u-7f3a" },
  "data": { },
  "evidence": [
    {
      "id": "ev-01JCD0X4",
      "source": "snowflake.account_usage.grants_to_users",
      "retrieved_at": "2026-11-10T10:21:44Z",
      "data_as_of": "2026-11-10T08:21:44Z",
      "ref": "s3://caa-evidence/2026/11/10/dx-01JCD0X1/ev-01JCD0X4.json"
    }
  ],
  "freshness": { "mode": "lagged", "max_lag_seconds": 7200 },
  "warnings": [ { "code": "LAGGED_SOURCE", "message": "Grants may be up to 2 hours old." } ],
  "error": null,
  "trace_id": "1-6730a1c8-5f2b"
}
```

| `status` | Meaning | Agent behaviour |
|---|---|---|
| `ok` | Complete answer | Use it |
| `partial` | Some sources failed or data was truncated; `warnings` say which | Use it, state the gap |
| `not_found` | The subject or object does not exist in that system | Treat as a finding, not an error |
| `denied` | Requester lacks scope for this subject or tool | Explain the limit; do not retry with other parameters |
| `error` | Tool failed; see `error.code`, `error.retryable` | Retry once if retryable, then say that system could not be checked |

### Error codes

| Code | Retryable | Meaning |
|---|---|---|
| `INVALID_INPUT` | no | Parameter failed validation |
| `SUBJECT_AMBIGUOUS` | no | More than one identity matched; `data.candidates` lists them |
| `SCOPE_DENIED` | no | Authorisation failed |
| `UPSTREAM_TIMEOUT` | yes | Source system did not answer in time |
| `UPSTREAM_AUTH` | no | Service credential rejected (page the on-call) |
| `UPSTREAM_THROTTLED` | yes | Source rate limit; `error.retry_after_seconds` set |
| `UPSTREAM_ERROR` | maybe | Any other source error; raw message is logged, not returned |
| `CONFIRMATION_REQUIRED` | no | Write tool called without a valid confirmation token |
| `NOT_ENABLED` | no | Tool or platform is switched off in this environment |

## 3. Authorisation model for tools

Scopes come from Entra ID group claims mapped in `config/scopes.yaml`.

| Scope | May call tools for | Typical members |
|---|---|---|
| `self` | Themselves only. Object-level tools (`scope: self` in the catalog) for any object. | All consumers |
| `support` | Any user | Platform helpdesk |
| `steward` | Users and policies of data products they own | Data stewards, data product owners |
| `platform` | Everything, including storage and auth-policy tools | Platform engineers |

Enforcement happens three times, none of them in the model: the API Gateway authorizer (who), the Gateway Cedar policy (may this requester call this tool for this `user`), and `caa_core.authz.check()` at the start of every handler. Details in [07-security-and-governance.md](07-security-and-governance.md).

Field-level rules: client IP (SF-09), other users' query text (SF-05/06) and full policy exception logic (IM-09) are removed for scopes below those listed in the catalog.

## 4. Phase 1 tool details

Each entry gives purpose, inputs, output `data`, source calls, logic and edge cases. Input types follow `specs/tool-catalog.yaml`.

---

### ID-01 `identity_resolve_user`

**Purpose.** One person has up to five names. Everything else depends on mapping them correctly, and identity mismatch is itself a frequent root cause.

**Output `data`**

```json
{
  "canonical_user_id": "u-7f3a",
  "entra":      { "found": true, "object_id": "…", "upn": "asha.rao@example.com", "sam_account_name": "arao", "account_enabled": true },
  "immuta":     { "found": true, "profile_id": 412, "iamid": "entra", "userid": "asha.rao@example.com", "disabled": false,
                  "external_user_ids": { "snowflake": "ASHA.RAO@EXAMPLE.COM", "databricks": null, "trino": null } },
  "snowflake":  { "found": true, "name": "ASHA.RAO@EXAMPLE.COM", "login_name": "ASHA.RAO@EXAMPLE.COM", "disabled": false },
  "databricks": { "checked": false },
  "starburst":  { "checked": false },
  "mismatches": []
}
```

**Logic**

1. Look the input up in Entra ID by `userPrincipalName`, `mail`, then `onPremisesSamAccountName`.
2. Immuta: `GET /bim/user?userid=<upn>`; if empty, retry with email and sAMAccountName. Read `externalUserIds` from the profile.
3. Snowflake: expected user name = Immuta's external Snowflake id if set, otherwise the Immuta `userid`. Run `get_user.sql`.
4. Record a mismatch when: the Snowflake user that exists does not equal the name Immuta maps to (code `IDN-003`); a system has no record (`IDN-001` / `IDN-002`); more than one live Snowflake user matches (`IDN-004`).
5. Cache 15 minutes keyed on the normalised input.

**Edge cases.** Service accounts and shared mailboxes resolve in Entra but must return `status: denied` for `self` requesters. Case differences between Snowflake `NAME` and Immuta `userid` are the classic silent mismatch: compare case-insensitively to find the row, then report whether they are *exactly* equal, because Immuta's mapping may be case-sensitive (**VERIFY** behaviour in your tenant).

---

### ID-02 `idp_get_user`, ID-03 `idp_get_user_groups`, ID-04 `idp_check_group_membership`

**Source.** Microsoft Graph v1.0, application permissions `User.Read.All`, `GroupMember.Read.All`.

| Tool | Call | Notes |
|---|---|---|
| ID-02 | `GET /users/{id}?$select=id,accountEnabled,userPrincipalName,mail,onPremisesSamAccountName,department,userType,onPremisesSyncEnabled,onPremisesLastSyncDateTime` and `GET /users/{id}/manager?$select=displayName,userPrincipalName` | `account_enabled=false` short-circuits most diagnoses (`IDN-005`). |
| ID-03 | `GET /users/{id}/transitiveMemberOf/microsoft.graph.group?$select=id,displayName&$top=999` with header `ConsistencyLevel: eventual` | Follow `@odata.nextLink`. Default filter keeps only names matching `config/group-prefixes.yaml`. To label `direct` versus `nested`, also call `GET /users/{id}/memberOf` and diff. |
| ID-04 | `POST /users/{id}/checkMemberGroups` body `{"groupIds":[…]}` (max 20 per call) | Resolve names to ids with `GET /groups?$filter=displayName eq '…'`. Unknown group name returns `is_member: null` with warning `GROUP_NOT_FOUND`. |

**Edge cases.** Users in hundreds of groups: return the filtered list and `total`. Dynamic groups: membership is rule-driven and can lag; ID-05 (Phase 2) exposes the rule. If AD is the authority and Entra is a sync target, group changes are subject to the directory sync cycle; report `last_directory_sync`.

---

### IM-01 `immuta_get_user`, IM-02 `immuta_get_user_entitlements`

**Source.** Immuta v1 BIM API. Authenticate once per container: `POST /bim/apikey/authenticate` with the service API key, then `Authorization: Bearer <token>`; cache the token until it expires.

| Step | Call |
|---|---|
| Find | `GET /bim/user?userid=<userid>` (filters also include `email`, `iamid`) |
| Aggregate view | `GET /bim/iam/{iamid}/user/{id}` returns `authorizations`, `permissions`, `profile`, `groups` (needs `USER_ADMIN` or `AUDIT`) |
| Groups | `GET /bim/iam/{iamid}/user/{userid}/groups` |
| Group attributes | `GET /bim/group/{groupId}` returns `authorizations` for that group |

**IM-02 output `data`**

```json
{
  "groups": [ { "name": "DM-SALES-CONSUMER", "iamid": "entra" } ],
  "attributes": [
    { "name": "AccountAccess", "values": ["A100", "A200", "A315"], "origin": "iam" },
    { "name": "PIAccess", "values": ["Standard"], "origin": "group", "via_group": "DM-PI-STANDARD" }
  ],
  "synced_from_iam": true
}
```

**Logic.** `origin` is derived by comparing `iamAuthorizations` (from the identity provider), `bimAuthorizations` (set inside Immuta) and attributes carried by groups. Immuta has no endpoint that returns attributes alone; they are the `authorizations` field of user and group objects.

**Why this matters.** The most common L1 fault is a group that exists in AD but has not reached Immuta. The engine compares ID-03 with IM-02 and reports each group as `in_both`, `ad_only` (sync lag or mapping problem, `DIR-003`) or `immuta_only`.

---

### IM-03 `immuta_find_data_source`, IM-04 `immuta_get_data_source`

| Tool | Calls | Notes |
|---|---|---|
| IM-03 | `GET /dataSource?searchText=<table>&schema=<schema>&size=25`; `GET /dataSource/sqlTableName/{shortName}` | A table can be registered more than once (per platform). Match on platform + remote database/schema/table from the data source's connection metadata. Zero matches = not registered in Immuta (`POL-001`). |
| IM-04 | `GET /dataSource/{dataSourceId}`; `GET /dataSource/{dataSourceId}/contacts` | Use `status`/`statusInfo` for health, `subscriptionPolicy`, `globalPolicies`, `deleted`. A disabled or unhealthy data source is `POL-002`. |

---

### IM-05 `immuta_get_subscription_status`

**Call.** `GET /dataSource/{dataSourceId}/access?searchText=<userid>&expandGroups=true`. Response users carry `state`, `approved`, `approvals`, `subscriptionId`.

**Output `data`**

```json
{ "state": "not_subscribed", "approved": null, "via": null, "expiration": null, "pending_approvers": [] }
```

`state` values to expect include `subscribed`, `owner`, `expert`, `pending`, `not_subscribed`. Map anything else to `unknown` and log it.

---

### IM-06 `immuta_get_subscription_policy` and IM-16 `immuta_explain_subscription_decision`

**IM-06** normalises whatever shape Immuta returns into a small condition tree, so IM-16 can evaluate it without knowing Immuta's JSON.

```json
{
  "policy_type": "automatic",
  "condition_tree": {
    "op": "AND",
    "children": [
      { "kind": "group", "name": "DM-SALES-CONSUMER" },
      { "op": "OR", "children": [
          { "kind": "attribute", "name": "Region", "value": "APAC" },
          { "kind": "attribute", "name": "Region", "value": "GLOBAL" } ] }
    ]
  },
  "plain_english": "Members of DM-SALES-CONSUMER whose Region attribute is APAC or GLOBAL are subscribed automatically."
}
```

`policy_type`: `automatic` (entitlement-driven), `approval` (individually approved), `anyone`, `none` (manual only). **VERIFY** the JSON of `subscriptionPolicy` and global policy definitions in your Immuta version and write the normaliser against recorded fixtures.

**IM-16** is a pure function `evaluate(condition_tree, entitlements) -> decision`:

```json
{
  "expected_access": "no",
  "satisfied_conditions": [ { "kind": "attribute", "name": "Region", "value": "APAC" } ],
  "unmet_conditions":     [ { "kind": "group", "name": "DM-SALES-CONSUMER" } ],
  "missing_groups": ["DM-SALES-CONSUMER"],
  "missing_attributes": []
}
```

Rules: for `OR`, report the cheapest unmet branch (fewest missing items). If the tree contains a construct the normaliser does not understand (custom SQL, purposes), return `expected_access: "unknown"` with the raw policy text in evidence, and never guess. Property-based tests cover the evaluator ([09](09-testing-and-evaluation.md)).

---

### IM-07 `immuta_get_user_policy_info`

**Call.** `GET /dataSource/{dataSourceId}/users/{profileId}/policyInfo` (permission `FETCH_POLICY_INFO`). Response fields: `visibilities`, `visibilityRuleApplies`, `masked`, `additionalFilters`. Optional `GET …/visibilityReport` (needs `GOVERNANCE` or ownership) adds counts.

This is Immuta's own computation of what the user will see, so it is preferred over re-deriving row and masking outcomes. EN-01 and EN-02 wrap it.

---

### IM-11 `immuta_get_data_source_tags`, IM-12 `immuta_get_integration_status`

| Tool | Calls | Notes |
|---|---|---|
| IM-11 | `GET /dataSource/{dataSourceId}/tags` (+ data dictionary for column-level tags, **VERIFY** endpoint) | `is_pi` = any tag in `config/pi-classification.yaml`. |
| IM-12 | `GET /integrations`; `GET /integrations/{id}/status` | Returns `status` and `validationResults`. Anything other than enabled and passing becomes platform finding `PLT-001` and is checked before any per-user work. |

---

### SF-01 to SF-08 (Snowflake)

SQL lives in [`sql/snowflake/`](../sql/snowflake/README.md). Common handler behaviour: key-pair connection as `CAA_DIAG_SVC`, role `CAA_DIAG_READER`, warehouse `CAA_DIAG_WH`, session query tag, 30 s statement timeout, bind variables only.

| Tool | SQL | Key output and logic |
|---|---|---|
| SF-01 `snowflake_get_user` | `get_user.sql` | `disabled`, `locked`, `expires_at`, `default_role`, `default_warehouse`, `default_secondary_roles`. A user whose `default_secondary_roles` is explicitly empty depends on the client running `USE SECONDARY ROLES ALL`. |
| SF-02 `snowflake_get_user_roles` | `get_user_roles.sql` | Direct and inherited roles with grant path. `immuta_role_present` when a role named `<PREFIX>_USER_<username>` exists (prefix from config). |
| SF-03 `snowflake_check_object_privileges` | `check_object_privileges.sql` | The three-link chain. `roles_with_full_chain`, `requires_secondary_roles`. |
| SF-04 `snowflake_list_accessible_tables` | `list_accessible_tables.sql` | Scoped to data-mesh databases; marks rows unusable when a parent `USAGE` is missing. |
| SF-05 `snowflake_get_failed_queries` | `get_failed_queries.sql` | Defaults `days=5`, `limit=10`. Adds `error_class` and redacted text. |
| SF-06 `snowflake_get_query_details` | `get_query_details.sql` | One query id; adds objects and policies referenced when available. |
| SF-07 `snowflake_get_table_policies` | `get_table_policies.sql` | Row access and masking policies attached; `immuta_managed`. |
| SF-08 `snowflake_get_table_status` | `get_table_status.sql` | `exists`, `table_type`, `recreated_recently`. |

**How Immuta and Snowflake fit together (drives SF-02 and SF-03).** With Immuta's Snowflake table grants feature, Immuta creates one Snowflake role per user (`<PREFIX>_USER_<username>`) and grants `SELECT` on subscribed tables to that role. The user's own functional role usually supplies warehouse usage. A query therefore succeeds only when the session has *both*: either the Immuta role is primary and has what it needs, or secondary roles are active (`USE SECONDARY ROLES ALL` or `DEFAULT_SECONDARY_ROLES`). SF-05 returns `secondary_role_stats` from query history so the engine can see what the failing session actually had.

**How common is this?** Since Snowflake behaviour change bundle 2024_08, a user whose `DEFAULT_SECONDARY_ROLES` was unset gets `('ALL')`, so most interactive sessions already have secondary roles active. The split-role failure (`SES-001`) therefore shows up mainly where the property was explicitly set to empty, where a client or connection string disables secondary roles, or where a session policy restricts them. The engine does not assume either way: it reads the user's setting (SF-01) and what the failing query actually ran with (SF-05). Confirm how your account and BI tools are set in CAA-003.

**SF-05 example `data`**

```json
{
  "queries": [
    {
      "query_id": "01b8a1c2-0001-9d3e-0000-12345678abcd",
      "start_time": "2026-11-10T04:12:09Z",
      "error_code": "002003",
      "error_message": "SQL compilation error: Object 'SALES.CURATED.ORDERS' does not exist or not authorized.",
      "error_class": "authorization_or_missing_object",
      "role_name": "ANALYST_APAC",
      "secondary_roles": [],
      "warehouse": "ANALYST_WH",
      "database": "SALES",
      "schema": "CURATED",
      "query_text_redacted": "select * from SALES.CURATED.ORDERS where region = ? limit ?"
    }
  ],
  "window": { "days": 5, "limit": 10 }
}
```

**Error classification.** `config/error-catalog.yaml` maps code and message pattern to a class and playbook. The seed list (**VERIFY** and extend from your own query history in CAA-003):

| Code / pattern | `error_class` | Playbook |
|---|---|---|
| `002003` "does not exist or not authorized" | `authorization_or_missing_object` | PB-01 |
| `003001` "Insufficient privileges" | `authorization` | PB-01 |
| `000606` "No active warehouse selected" | `session_no_warehouse` | PB-09 |
| "does not have a current database" / "current schema" | `session_no_context` | PB-09 |
| `001003` syntax error, `000904` invalid identifier | `sql_error` (invalid identifier may be schema drift) | PB-08 |
| `000630` statement timeout | `compute_timeout` | PB-09 |
| Resource monitor / warehouse suspended messages | `compute_quota` | PB-09 |
| External volume / remote file access denied messages | `storage_access` | PB-08 |
| Login `390100` bad credentials, `390422` IP not allowed | `login_failure` | PB-04 |

---

### EN-01 `entitlement_get_row_visibility`

**Purpose.** "Which accounts can I see?" answered from policy, without touching the data.

**Inputs.** `user`, `table`, `platform`.

**Logic**

1. Resolve the Immuta data source (IM-03) and call IM-07.
2. If `row_filter_applies` is false: `rls_applies=false`, `sees_all_rows=true`.
3. Otherwise look up the table's RLS model in `config/rls-models.yaml`:
   - **`attribute`**: the policy compares a column with a user attribute (for example `account_id` in attribute `AccountAccess`). `visible_values` = the user's values for that attribute from IM-02. A wildcard value configured as "all" sets `sees_all_rows`.
   - **`lookup_table`**: the policy joins to an entitlement mapping table. Run the configured parameterised query against that mapping table for this user (the service role needs `SELECT` on the mapping table only).
   - **`unknown`**: return the filter text from Immuta in evidence, set `visible_values: null`, warning `RLS_MODEL_UNMAPPED`.
4. If the user is subscribed but `visible_values` is empty, set `sees_no_rows=true` (root cause `POL-006`): this is the "query runs, returns nothing" case.

**Output `data`**

```json
{
  "rls_applies": true,
  "scope_dimension": "account_id",
  "visible_values": ["A100", "A200", "A315"],
  "visible_count": 3,
  "sees_all_rows": false,
  "sees_no_rows": false,
  "granted_by": [ { "attribute": "AccountAccess", "origin": "iam" } ],
  "policy_plain_english": "Rows are limited to accounts listed in your AccountAccess attribute."
}
```

**Sensitivity.** Account identifiers are entitlement data. Return them to `self` (their own) and `support` and above. Cap the list at 200 values and return `visible_count`.

---

### EN-02 `entitlement_get_pi_access`

**Logic**

1. PI columns = columns whose tags are in `config/pi-classification.yaml` (IM-11).
2. For each PI column, state = `masked` if it appears in IM-07 `masked_columns`, else `clear`.
3. Cross-check with SF-07: a PI column that Immuta masks must have a masking policy attached in Snowflake. A gap is an enforcement finding (`ENF-003`), reported to governance and not as "you have PI access".
4. `unmask_requires` comes from the access contract (DP-02) and, when available, the policy's exception condition (IM-09, Phase 2).
5. Without `table`, summarise across subscribed data sources: counts of PI columns clear versus masked per data product, capped at 50 data sources.

**Output `data`**

```json
{
  "has_pi_entitlement": false,
  "pi_entitlement_source": null,
  "columns": [
    { "column": "CUSTOMER_EMAIL", "pi_category": "Contact", "state": "masked", "masking_type": "hash", "unmask_requires": "AD group DM-PI-SALES" },
    { "column": "NATIONAL_ID", "pi_category": "Government ID", "state": "masked", "masking_type": "null", "unmask_requires": "AD group DM-SPI-SALES plus approved purpose" }
  ]
}
```

---

### EN-03 `entitlement_get_access_summary`

Fan-out to ID-01, ID-03, IM-02, SF-01, SF-02 and DP-04 in parallel with a 10 s budget; any source that fails makes the result `partial`. `anomalies` lists cross-system inconsistencies found on the way (group in AD but not Immuta, Immuta role missing in Snowflake, user disabled in one system). Cached 5 minutes per subject.

---

### DP-01, DP-02, DP-04 (catalog and telemetry)

These depend on systems this design does not know yet. They are specified as **ports** with a required output shape; the adapter is written once the source is confirmed (CAA-004).

```python
class CatalogPort(Protocol):
    def search(self, query: str, limit: int) -> list[DataProductSummary]: ...
    def get(self, data_product_id: str) -> DataProduct: ...           # includes access_contract
    def find_by_table(self, platform: str, table: TableRef) -> DataProduct | None: ...

class TelemetryPort(Protocol):
    def user_access(self, user: CanonicalUser, platform: str | None) -> list[UserAccessRow]: ...
```

`access_contract` is the statement of what a consumer needs:

```json
{ "groups": ["DM-SALES-CONSUMER"], "attributes": { "Region": ["APAC", "GLOBAL"] },
  "pi_group": "DM-PI-SALES", "request_route": { "system": "iga", "url": "https://…", "item": "DM-SALES-CONSUMER" } }
```

If the catalog does not hold access contracts, they are kept in `config/access-contracts/<data_product>.yaml` and the engine cross-checks them against the live Immuta policy (IM-06), flagging disagreement as `POL-007`.

---

### DX-01 `diagnose_table_access`

The main tool. Specified in full in [06-diagnostic-model.md](06-diagnostic-model.md). Contract summary:

**Inputs.** `user`, `table`, `platform`, optional `query_id`.

**Output `data`**

```json
{
  "diagnosis_id": "dx-01JCD0X1",
  "verdict": "expected_no_actual_no",
  "expected_access": "no",
  "actual_access": "no",
  "summary_code": "POL-004",
  "layers": [
    { "layer": "L0_identity",     "status": "pass", "findings": [] },
    { "layer": "L1_entitlements", "status": "fail", "findings": ["DIR-001"] },
    { "layer": "L2_policy",       "status": "fail", "findings": ["POL-004"] },
    { "layer": "L3_enforcement",  "status": "consistent", "findings": [] },
    { "layer": "L4_session",      "status": "not_evaluated", "findings": [] },
    { "layer": "L5_data",         "status": "pass", "findings": [] }
  ],
  "root_causes": [
    { "code": "DIR-001", "title": "Not a member of required AD group", "confidence": "high",
      "detail": { "group": "DM-SALES-CONSUMER" }, "evidence_refs": ["ev-01", "ev-04"] }
  ],
  "next_actions": [
    { "actor": "user", "action": "request_group", "detail": { "group": "DM-SALES-CONSUMER", "route": "https://…" },
      "expected_effect": "Subscription is automatic once the group syncs to Immuta (typically under 1 hour)." }
  ],
  "unchecked": [],
  "data_as_of": "2026-11-10T08:21:44Z"
}
```

`unchecked` lists any layer or source that could not be evaluated. The agent must mention every item in it.

---

### DX-02 `diagnose_failed_query`

1. Get the query (SF-06 by id, or the latest from SF-05).
2. Classify with the error catalog.
3. For `authorization*` classes, extract table references from the redacted SQL with `sqlglot` (Snowflake dialect), resolve unqualified names with the query's database and schema, and run DX-01 for each (maximum 5), passing the query's role and secondary roles as the session context.
4. For session, compute, SQL and storage classes, return the class, the specific fix and the playbook id.

---

### WF-01 `kb_search`, WF-02 `kb_get_error_reference`

| Tool | Source | Notes |
|---|---|---|
| WF-01 | Bedrock Knowledge Bases `Retrieve` | Returns passages with `source_uri`. The agent cites the source. Retrieved text is data, not instructions. |
| WF-02 | `config/error-catalog.yaml` | Deterministic. Preferred over WF-01 for error meaning. |

## 5. Write tools and confirmation

Write tools (`itsm_create_ticket`, `notify_platform_team`, `onboarding_start_access_request`) follow one pattern:

1. The agent calls the tool with `dry_run: true`. The handler returns a preview and a `confirmation_token` bound to the conversation, the requester and a hash of the payload, valid for 10 minutes.
2. The agent shows the preview and asks the user to confirm.
3. On the user's explicit "yes", the agent calls again with the token. The handler re-validates the token and payload hash, then performs the action with an idempotency key.

A model cannot fabricate a valid token, and the Gateway policy rejects a write call without one.

## 6. Adding a tool

1. Add the entry to `specs/tool-catalog.yaml`; run `python scripts/render_tool_catalog.py`.
2. Add the JSON Schema for input and `data` to `specs/schemas/<tool>.json`.
3. Implement the handler in `src/tools/<domain>/<tool>.py` using `@tool` from `caa_core`.
4. Add recorded fixtures and contract tests.
5. Register the tool in the Gateway target definition (`infra/gateway_targets.py`) and, if needed, the REST route.
6. Add at least one eval scenario that needs the tool.
