# User Stories: Consumer Access Assistant

Epic: [`EPIC.md`](EPIC.md) &nbsp;|&nbsp; Design: [`docs/`](docs/01-solution-overview.md) &nbsp;|&nbsp; Tools: [`docs/03-tool-catalog.md`](docs/03-tool-catalog.md)

## How to use this file

- Each story is sized to be created as one tracker item. Copy the title, the story sentence, the acceptance criteria and the notes.
- **Tools** lists tool ids from the catalog. **Depends** lists stories that must finish first.
- **Pts** are relative story points (1, 2, 3, 5, 8) as a first guess; re-estimate with the team after spike CAA-003.
- Acceptance criteria use Given / When / Then. Every tool story also inherits the tool definition of done in `docs/09` section 6; it is not repeated in each story.
- Personas (`p01` to `p17`) are the seeded test users in `docs/09` section 2.

## Story index

| ID | Title | Phase | Pts |
|---|---|---|---|
| CAA-001 | Repository, standards and CI skeleton | 0 | 3 |
| CAA-002 | Hosting readiness: Region, Bedrock, AgentCore, approvals | 0 | 3 |
| CAA-003 | Spike: verify upstream APIs and SQL, record fixtures | 0 | 8 |
| CAA-004 | Spike: catalog and telemetry sources | 0 | 3 |
| CAA-005 | Baseline metrics and volumes | 0 | 2 |
| CAA-006 | Seed non-prod personas and objects | 0 | 5 |
| CAA-007 | Provision read-only service identities | 0 | 5 |
| CAA-008 | Configuration framework and scope mapping | 0 | 3 |
| CAA-009 | `caa_core` foundation | 0 | 8 |
| CAA-010 | Baseline infrastructure | 0 | 5 |
| CAA-101 | Resolve a user across systems | 1 | 5 |
| CAA-102 | Directory user, groups and membership check | 1 | 5 |
| CAA-110 | Immuta connector, user and entitlements | 1 | 5 |
| CAA-111 | Immuta data source lookup, health and integration status | 1 | 3 |
| CAA-112 | Subscription status and policy normaliser | 1 | 8 |
| CAA-113 | Subscription policy evaluator | 1 | 5 |
| CAA-114 | Per-user policy outcome and column tags | 1 | 3 |
| CAA-120 | Snowflake connector, user and roles | 1 | 5 |
| CAA-121 | Privilege chain and accessible tables | 1 | 5 |
| CAA-122 | Failed queries, query details and error catalog | 1 | 5 |
| CAA-123 | Table policies and table status | 1 | 3 |
| CAA-130 | Row visibility: which accounts can I see | 1 | 5 |
| CAA-131 | PI access | 1 | 5 |
| CAA-132 | Access summary | 1 | 3 |
| CAA-140 | Data product catalog adapter | 1 | 5 |
| CAA-141 | Telemetry adapter: what the user can access | 1 | 3 |
| CAA-150 | Diagnosis engine core | 1 | 8 |
| CAA-151 | Diagnose table access | 1 | 8 |
| CAA-152 | Diagnose a failed query | 1 | 5 |
| CAA-160 | MCP Gateway, tool registration and authorisation policy | 1 | 8 |
| CAA-161 | REST API projection | 1 | 3 |
| CAA-162 | Knowledge base and search tool | 1 | 3 |
| CAA-170 | Orchestrator agent | 1 | 8 |
| CAA-171 | Chat API with SSO and streaming | 1 | 5 |
| CAA-172 | Answer formatting and guardrails | 1 | 5 |
| CAA-180 | Evaluation harness and golden set | 1 | 8 |
| CAA-181 | Observability baseline | 1 | 5 |
| CAA-182 | Security review and go-live gate | 1 | 5 |
| CAA-183 | MVP pilot | 1 | 3 |
| CAA-201 | Login failure diagnosis | 2 | 3 |
| CAA-202 | Change history: "it worked yesterday" | 2 | 5 |
| CAA-203 | Compare two users | 2 | 3 |
| CAA-204 | Row and masking diagnosis with policy detail | 2 | 5 |
| CAA-205 | Group details and source attributes | 2 | 2 |
| CAA-206 | Immuta audit, subscriptions list and access requests | 2 | 5 |
| CAA-207 | Warehouse, Iceberg and data product health | 2 | 5 |
| CAA-210 | Request status from ITSM and identity governance | 2 | 5 |
| CAA-211 | Tickets and escalations with confirmation | 2 | 5 |
| CAA-212 | Governance findings for over-entitlement | 2 | 3 |
| CAA-220 | Monitoring framework and findings tools | 2 | 5 |
| CAA-221 | Checks: integration health, failure spike, canary query | 2 | 5 |
| CAA-222 | Checks: entitlement drift and orphaned access | 2 | 8 |
| CAA-223 | Check: sync lag | 2 | 5 |
| CAA-224 | Alert routing and estate insight dashboard | 2 | 3 |
| CAA-230 | Web chat UI | 2 | 5 |
| CAA-231 | Teams or Slack bot | 2 | 5 |
| CAA-232 | Feedback loop and online evaluation | 2 | 3 |
| CAA-233 | Steward view: who can see my data product | 2 | 5 |
| CAA-234 | Runbooks and support hand-over | 2 | 3 |
| CAA-301 | Platform adapter interface | 3 | 5 |
| CAA-302 | Databricks tools | 3 | 8 |
| CAA-303 | Databricks in the diagnosis engine | 3 | 5 |
| CAA-304 | Starburst tools and adapter | 3 | 8 |
| CAA-305 | Producer storage tools and Iceberg staleness check | 3 | 5 |
| CAA-306 | Platform specialist sub-agents | 3 | 5 |
| CAA-307 | Access snapshots, diff over time and remaining tools | 3 | 5 |
| CAA-308 | Decision and build: on-behalf-of probe | 3 | 3 |
| CAA-401 | Onboarding prerequisites | 4 | 5 |
| CAA-402 | Live onboarding checklist | 4 | 5 |
| CAA-403 | Sample code and connection profiles | 4 | 8 |
| CAA-404 | Guided access requests | 4 | 5 |
| CAA-405 | Onboarding conversation and evals | 4 | 5 |
| CAA-406 | Onboarding measures | 4 | 2 |

---

# Phase 0: Foundations

### CAA-001 Repository, standards and CI skeleton
**As a** developer, **I want** a repository with agreed structure, tooling and a CI pipeline, **so that** every later story starts from the same base.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F0 | 3 | - | - |

**Acceptance criteria**
- Given the layout in `docs/10` section 3, when the repo is created, then the packages `caa_core`, `caa_tools`, `caa_agent`, `caa_api`, `caa_monitor`, `infra` exist with empty tests passing.
- Given a pull request, when CI runs, then ruff, mypy, pytest, secret scan, schema validation of `config/` and `specs/`, and the tool-catalog render check all execute.
- Given the IaC decision (CDK or Terraform) and CI choice, when they are made, then they are recorded in an ADR and in `CLAUDE.md`.
- `CLAUDE.md` and `.github/copilot-instructions.md` are present and reviewed by the team.

---

### CAA-002 Hosting readiness: Region, Bedrock, AgentCore, approvals
**As an** architect, **I want** confirmation that the chosen agent platform and model are available and approved, **so that** ADR-001 can be accepted or its fallback triggered.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F0 | 3 | - | - |

**Acceptance criteria**
- The approved AWS Region is confirmed to offer AgentCore Runtime, Gateway, Identity, Memory, Policy and the chosen Claude model; gaps are listed.
- Security and privacy approve processing of entitlement metadata by the model service, in writing.
- A hello-world agent is deployed to AgentCore Runtime in `dev` and calls one Lambda tool through the Gateway with a user JWT.
- ADR-001 is marked Accepted, or the fallback design is adopted and the affected stories re-estimated.

---

### CAA-003 Spike: verify upstream APIs and SQL, record fixtures
**As a** developer, **I want** every upstream call and SQL template run against non-prod and its response recorded, **so that** tools are built on real shapes and not on documentation.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F0 | 8 | CAA-006, CAA-007 | All Phase 1 |

**Acceptance criteria**
- Each item V1 to V17 in `docs/12` section 3 has a result: confirmed, corrected, or not available with an alternative.
- Each SQL file in `sql/snowflake/` runs under `CAA_DIAG_READER`; corrections are committed.
- Sanitised fixtures for every Phase 1 call are committed under `tests/fixtures/`, produced by `scripts/sanitise_fixture.py`.
- The minimum Immuta permission set for the service user is documented.
- Observed latency of each `ACCOUNT_USAGE` view is recorded in `config/sync-windows.yaml`.
- The top 20 Snowflake failure codes from the last 30 days are added to `config/error-catalog.yaml`.
- `specs/tool-catalog.yaml` entries with `verify: true` for Phase 1 are updated and the flag removed.

---

### CAA-004 Spike: catalog and telemetry sources
**As a** developer, **I want** to know where data product metadata, access requirements and access telemetry live, **so that** the catalog and telemetry adapters can be designed.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F0 | 3 | - | DP-01, DP-02, DP-04 |

**Acceptance criteria**
- Questions Q9 and Q10 in `docs/12` are answered with system, interface, schema, freshness and owner.
- A decision is recorded for each port: adapter to an existing API or table, or config-file fallback.
- Sample responses are saved as fixtures.

---

### CAA-005 Baseline metrics and volumes
**As a** product owner, **I want** current access-ticket volumes and resolution times, **so that** benefits can be measured.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F0 | 2 | - | - |

**Acceptance criteria**
- Monthly access-related ticket count, median resolution time, re-assignment rate and top categories for the last 6 months are documented.
- Expected user numbers and peak concurrency are estimated and entered in `docs/08` NFRs.
- The success measures in `docs/01` section 9 have baselines.

---

### CAA-006 Seed non-prod personas and objects
**As a** tester, **I want** seeded users and tables covering each diagnosis outcome, **so that** tools, engine and agent can be tested repeatably.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F0 | 5 | - | - |

**Acceptance criteria**
- Personas `p01` to `p17` and the object fixtures in `docs/09` section 2 exist in the non-prod directory, Immuta and Snowflake.
- A script or documented procedure recreates them.
- Each persona's intended verdict is confirmed manually once and recorded.

---

### CAA-007 Provision read-only service identities
**As a** platform owner, **I want** the assistant's service identities created with least privilege, **so that** it can read metadata and nothing else.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F0 | 5 | - | - |

**Acceptance criteria**
- Snowflake: `sql/snowflake/00_service_role_setup.sql` reviewed and run; key-pair in Secrets Manager; network policy applied.
- Immuta: service user and API key created with the agreed permissions.
- Entra ID: app registration with `User.Read.All` and `GroupMember.Read.All` admin-consented.
- Each platform owner signs off the privilege list in `docs/07` section 4.
- A test from a Lambda in `dev` authenticates to each system.
- No identity has any write privilege on data-mesh objects, verified by the owner.

---

### CAA-008 Configuration framework and scope mapping
**As a** developer, **I want** typed, validated configuration, **so that** organisation-specific rules are data and not code.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F0 | 3 | CAA-001 | - |

**Acceptance criteria**
- Each file in `config/examples/` has a Pydantic model and a schema; CI fails on unknown keys.
- Real values for scopes, group prefixes, attribute map, data-mesh scope and Immuta settings are filled in for `dev`.
- Scope groups are created in Entra ID and mapped; privacy and security have agreed who gets `support` and `steward`.
- `config/` has CODEOWNERS.

---

### CAA-009 `caa_core` foundation
**As a** developer, **I want** the shared library that every tool uses, **so that** contracts, authorisation and audit are uniform.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F0 | 8 | CAA-001, CAA-008 | - |

**Acceptance criteria**
- `@tool` decorator provides input validation, authorisation, envelope, evidence capture, timing, audit log and error mapping as in `docs/10` section 4.1.
- `authz.check()` implements the scope rules in `docs/04` section 3, including field filtering, with unit tests for every scope and tool-scope combination.
- `identifiers.parse_table()` accepts valid names per platform and rejects everything else (fuzz tested).
- `redaction.redact_sql()` replaces string and numeric literals and strips comments while preserving identifiers.
- A tool that returns no evidence fails its contract test.
- A local CLI can invoke any registered tool with a fake requester context.

---

### CAA-010 Baseline infrastructure
**As a** developer, **I want** the shared AWS resources deployed, **so that** tools have somewhere to run.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F0 | 5 | CAA-001, CAA-002 | - |

**Acceptance criteria**
- IaC deploys to `dev`: VPC attachments and endpoints, KMS key, Secrets Manager entries, DynamoDB tables (`caa-cache`, `caa-diagnoses`, `caa-findings`), S3 buckets (`caa-evidence`, `caa-snapshots`), log groups, Lambda layer for `caa_core`.
- Network paths to Snowflake, Immuta and Microsoft Graph work from a Lambda in the VPC, by the route agreed with the network team.
- Buckets and tables are encrypted, private and have the retention in `docs/02` section 3.4.
- A pipeline deploys on merge to `main`.

---

# Phase 1: MVP

## F1 Identity and directory

### CAA-101 Resolve a user across systems
**As a** support engineer, **I want** one lookup that finds a person in the directory, Immuta and Snowflake, **so that** every diagnosis starts from the right identities and mismatches are caught.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F1 | 5 | CAA-009, CAA-102, CAA-110, CAA-120 | ID-01 |

**Acceptance criteria**
- Given a UPN, email or sAMAccountName, when the tool runs, then it returns the identity in each system or `found: false` per system.
- Given persona `p07`, then `immuta.found` is false and mismatch `IDN-001` is reported.
- Given persona `p08`, then mismatch `IDN-003` is reported with both names.
- Given an input matching two live Snowflake users, then status is `partial` with `SUBJECT_AMBIGUOUS` candidates.
- Results are cached for 15 minutes; a `self` requester resolving another person gets `denied`.

---

### CAA-102 Directory user, groups and membership check
**As a** consumer, **I want** to see which data-mesh AD groups I am in, **so that** I know whether I hold the group a data product needs.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F1 | 5 | CAA-007, CAA-009 | ID-02, ID-03, ID-04 |

**Acceptance criteria**
- Given a user, `idp_get_user` returns enabled status, UPN, mail, sAMAccountName, department and last directory sync.
- `idp_get_user_groups` returns transitive memberships filtered by configured prefixes, labelled direct or nested, and pages past 999 groups.
- `idp_check_group_membership` returns yes or no for up to 20 groups, and a warning for an unknown group name.
- Given persona `p09`, `account_enabled` is false.
- Graph throttling (429) is retried with backoff and surfaces as `UPSTREAM_THROTTLED` if it persists.

---

## F2 Immuta

### CAA-110 Immuta connector, user and entitlements
**As a** consumer, **I want** to see the groups and attributes Immuta holds for me, **so that** I can tell whether my entitlements have reached the system that decides access.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F2 | 5 | CAA-003, CAA-007, CAA-009 | IM-01, IM-02 |

**Acceptance criteria**
- The connector authenticates with the service API key, caches the bearer token, and exposes read methods only.
- `immuta_get_user` returns profile id, IAM id, disabled flag and external user id mappings, or `not_found`.
- `immuta_get_user_entitlements` returns groups and attributes, each attribute with `origin` (`iam`, `immuta`, `group`) and `via_group` where relevant.
- Attribute values flagged sensitive in config are not written to logs.
- Given persona `p05`, the required group is absent from the Immuta result while present in the directory result.

---

### CAA-111 Immuta data source lookup, health and integration status
**As a** support engineer, **I want** to map a table to its Immuta data source and see whether Immuta and its integrations are healthy, **so that** platform faults are ruled out first.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F2 | 3 | CAA-110 | IM-03, IM-04, IM-12 |

**Acceptance criteria**
- Given `SALES.CURATED.ORDERS` and platform `snowflake`, the matching data source id is returned; given the unregistered fixture, zero matches are returned.
- `immuta_get_data_source` returns enabled, health status and detail, owners and policy names.
- `immuta_get_integration_status` returns each integration's status and validation tests, cached for 2 minutes.
- A table registered for two platforms returns two matches distinguished by platform.

---

### CAA-112 Subscription status and policy normaliser
**As a** consumer, **I want** to know whether I am subscribed to a data source and what its policy requires, **so that** I know what to ask for.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F2 | 8 | CAA-111 | IM-05, IM-06 |

**Acceptance criteria**
- `immuta_get_subscription_status` returns state, approval info, how access was obtained and expiry for a user and data source.
- `immuta_get_subscription_policy` converts the policy into the condition tree of `docs/06` section 4 and a plain-English sentence.
- The normaliser handles the global subscription policies in use in the tenant that cover at least 80% of data sources (list agreed in CAA-003); anything else becomes an `unsupported` node carrying the raw text.
- Normaliser tests run against recorded fixtures for each supported policy shape.
- Given persona `p15`, state is `pending` and approvers are listed.

---

### CAA-113 Subscription policy evaluator
**As a** governance lead, **I want** the "should this user have access" decision computed by tested code, **so that** the assistant never guesses.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F2 | 5 | CAA-112 | IM-16 |

**Acceptance criteria**
- Given a condition tree and entitlements, the evaluator returns `yes`, `no`, `approval_required` or `unknown` with satisfied and unmet conditions and the missing groups and attributes.
- For an `OR`, the reported gap is the branch with the fewest missing items.
- Any `unsupported` node that affects the outcome yields `unknown`, never `yes`.
- Property-based tests cover the rules in `docs/09` section 3; branch coverage of the evaluator is 100%.
- Given personas `p03` and `p04`, the missing group and missing attribute value are named exactly.

---

### CAA-114 Per-user policy outcome and column tags
**As a** consumer, **I want** to know what Immuta will filter or mask for me on a table, **so that** unexpected results can be explained.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F2 | 3 | CAA-111 | IM-07, IM-11 |

**Acceptance criteria**
- `immuta_get_user_policy_info` returns whether a row filter applies, the filters, masked columns and visibilities for a user and data source.
- `immuta_get_data_source_tags` returns column tags and marks columns as PI using `config/pi-classification.yaml`.
- Given personas `p12` and `p13`, the same PI column is masked for one and clear for the other.

---

## F3 Snowflake

### CAA-120 Snowflake connector, user and roles
**As a** consumer, **I want** to see my Snowflake account status and roles, **so that** I can tell whether the platform side of my access is in place.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F3 | 5 | CAA-003, CAA-007, CAA-009 | SF-01, SF-02 |

**Acceptance criteria**
- The connector uses key-pair auth, the diagnostics role and warehouse, sets a query tag with tool name and trace id, a 30 s statement timeout, and bind variables only.
- `snowflake_get_user` returns disabled, locked, expiry, default role, default warehouse, default secondary roles and last login; `not_found` when absent.
- `snowflake_get_user_roles` returns direct and inherited roles with grant path, flags the Immuta-managed role using the configured prefix, and includes `PUBLIC`.
- Every response carries `freshness.mode = lagged` and `data_as_of`.
- Given persona `p16`, `locked` is true.

---

### CAA-121 Privilege chain and accessible tables
**As a** consumer, **I want** to know which tables I can read in Snowflake and, for one table, which role gives me each required privilege, **so that** I can see exactly where the platform side stops.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F3 | 5 | CAA-120 | SF-03, SF-04 |

**Acceptance criteria**
- `snowflake_check_object_privileges` returns database usage, schema usage and table select with the supplying roles, the roles that alone hold the full chain, and `requires_secondary_roles`.
- Given persona `p02`, `requires_secondary_roles` is true; given `p06`, `table_select` is false.
- `snowflake_list_accessible_tables` returns only objects in `config/data-mesh-scope.yaml`, with `total` and `truncated`, and marks rows unusable when parent usage is missing.
- Database-role and future-grant handling matches what CAA-003 found for the platform.

---

### CAA-122 Failed queries, query details and error catalog
**As a** consumer, **I want** my recent failed queries with a plain reason for each, **so that** I can see whether the failures are access-related.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F3 | 5 | CAA-120 | SF-05, SF-06, WF-02 |

**Acceptance criteria**
- With defaults, `snowflake_get_failed_queries` returns the last 10 failed queries in the last 5 days with error code, message, error class, role, secondary roles, warehouse and redacted text.
- No string or numeric literal from the original query text appears in any output or log.
- `snowflake_get_query_details` returns one query with objects and policies referenced when available; a `self` requester asking for another user's query id gets `denied`.
- `kb_get_error_reference` returns class, meaning, likely causes and playbook from `config/error-catalog.yaml`; an unknown error returns class `unclassified`.
- A query that failed inside the view's lag is reported as not yet visible, with the lag stated.

---

### CAA-123 Table policies and table status
**As a** support engineer, **I want** to see the policies attached to a table and whether it was recently recreated, **so that** enforcement gaps and lost grants are visible.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F3 | 3 | CAA-120 | SF-07, SF-08 |

**Acceptance criteria**
- `snowflake_get_table_policies` lists row access and masking policies with columns and marks those managed by Immuta.
- `snowflake_get_table_status` returns existence, type, Iceberg flag, owner, created and altered times, and `recreated_recently` using the configured window.
- Given the recreated-table fixture, `recreated_recently` is true and the dropped version appears in `history`.
- A view is found when the name is not a table.

---

## F4 Entitlement answers

### CAA-130 Row visibility: which accounts can I see
**As a** consumer, **I want** to ask which accounts I can see in a table, **so that** I understand why my results are limited without anyone reading the data for me.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F4 | 5 | CAA-114, CAA-110 | EN-01 |

**Acceptance criteria**
- Given a table with an attribute-based row policy and persona `p11`, the tool returns exactly the persona's account values and the attribute that grants them.
- Given a lookup-table model, values come from the configured mapping table through a parameterised query.
- Given persona `p10`, `sees_no_rows` is true.
- Given a table with no RLS model configured, the result carries the policy text, `visible_values: null` and warning `RLS_MODEL_UNMAPPED`.
- The tool issues no query against any data product table (verified by Snowflake query tag audit in the integration test).
- Lists are capped at the configured maximum with `visible_count` accurate.

---

### CAA-131 PI access
**As a** consumer, **I want** to know which personal-information columns are masked for me and what would unmask them, **so that** I do not mistake masking for bad data.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F4 | 5 | CAA-114, CAA-123 | EN-02 |

**Acceptance criteria**
- Given a table, each PI column is listed with category, `clear` or `masked`, masking type and `unmask_requires`.
- Given no table, a summary across the user's subscribed data sources is returned, capped at 50.
- Given the fixture where Immuta masks a column but Snowflake has no masking policy attached, an enforcement finding `ENF-003` is raised and the column is not reported as clear.
- Given personas `p12` and `p13`, `has_pi_entitlement` is false and true respectively.

---

### CAA-132 Access summary
**As a** consumer, **I want** one overview of my identity, groups, attributes, roles and data products, **so that** I can answer "what access do I have" in one step.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F4 | 3 | CAA-101, CAA-102, CAA-110, CAA-120, CAA-141 | EN-03 |

**Acceptance criteria**
- The tool calls its sources in parallel within a 10 s budget and returns `partial` with a warning when one fails.
- `anomalies` lists cross-system inconsistencies (group in directory but not Immuta; Immuta role missing in Snowflake; disabled in one system).
- The result fits the 16 KB limit; long lists are summarised with counts.
- Cached for 5 minutes per subject.

---

## F5 Catalog and telemetry

### CAA-140 Data product catalog adapter
**As a** consumer, **I want** to find a data product and see what access it requires, **so that** I can request the right thing.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F5 | 5 | CAA-004, CAA-009 | DP-01, DP-02 |

**Acceptance criteria**
- `CatalogPort` is implemented against the source chosen in CAA-004, or the config-file fallback.
- `catalog_search_data_products` finds a product by name, keyword or table.
- `catalog_get_data_product` returns owner, steward, format, platforms, tables and the access contract with request routes.
- When a contract exists both in the catalog and as a live Immuta policy and they disagree, `POL-007` is reported.

---

### CAA-141 Telemetry adapter: what the user can access
**As a** consumer, **I want** the list of tables and data products I have access to, **so that** I can see my inventory quickly.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F5 | 3 | CAA-004, CAA-009 | DP-04 |

**Acceptance criteria**
- `TelemetryPort` is implemented against the telemetry store identified in CAA-004.
- The tool returns data products and tables per platform with `as_of`.
- When telemetry is unavailable, the tool falls back to `snowflake_list_accessible_tables` grouped by data product and says so in a warning.

---

## F6 Diagnosis engine

### CAA-150 Diagnosis engine core
**As a** developer, **I want** the layered evaluation, verdict matrix, root cause catalog and evidence model in a pure library, **so that** verdicts are deterministic and testable without a model or cloud services.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F6 | 8 | CAA-009, CAA-113 | - |

**Acceptance criteria**
- The engine implements layers L0 to L5, expected/actual/session derivation, the verdict matrix, the propagation rule and the lag rule exactly as in `docs/06`.
- `config/root-causes.yaml` holds every code in `docs/06` section 3 with title, owner and action template; unknown codes fail validation.
- The verdict function is tested exhaustively over its input combinations.
- With any single source failing, the engine returns a result with that layer `not_evaluated` and listed in `unchecked`.
- Every root cause in a result references at least one evidence id.
- The engine has no imports from AWS SDKs or the agent package.

---

### CAA-151 Diagnose table access
**As a** consumer, **I want** one check that tells me whether I should have access to a table, whether I do, and what to do, **so that** I do not need to understand five systems.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F6 | 8 | CAA-150, CAA-101, CAA-102, CAA-110 to 114, CAA-120 to 123 | DX-01 |

**Acceptance criteria**
- For each persona `p01` to `p17` and each object fixture, the tool returns the verdict and root causes listed in `docs/09` section 2.
- The result includes `next_actions` with actor, the exact group, attribute, command or route, and expected effect.
- The diagnosis and evidence are stored and retrievable by `diagnosis_id` for 400 days.
- p95 latency is under 15 s against non-prod sources.
- Given persona `p14`, a governance finding is written and `user_message_policy` is `neutral`.
- Given a change inside the propagation window, the root cause is `ENF-005` or `DIR-003` with medium confidence and a re-check time, not an escalation.
- A CLI demo runs the diagnosis for any persona without the agent (milestone M1).

---

### CAA-152 Diagnose a failed query
**As a** consumer, **I want** to paste a query id or ask about my last failed query, **so that** I learn whether it was an access problem and how to fix it.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F6 | 5 | CAA-151, CAA-122 | DX-02 |

**Acceptance criteria**
- Given a query id, the tool returns the error class and, for authorisation classes, a table-access diagnosis for each referenced table (maximum 5) using the query's role and secondary roles as session context.
- Table references are extracted from the redacted SQL, with unqualified names resolved from the query's database and schema.
- Given a syntax-error query, the result is `QRY-001` and states that access was not the cause.
- Given no query id, the most recent failed query is used and identified in the result.

---

## F7 Tool platform

### CAA-160 MCP Gateway, tool registration and authorisation policy
**As an** agent developer, **I want** all tools available on one MCP endpoint with scope rules enforced centrally, **so that** any agent can use them safely.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F7 | 8 | CAA-002, CAA-009, CAA-010 | All Phase 1 |

**Acceptance criteria**
- Tool definitions for the Gateway are generated from the Pydantic models and `specs/tool-catalog.yaml`; a CI check fails if they drift.
- The Gateway validates the user JWT; the requester's UPN and scopes reach the Lambda in the invocation context, not as tool input.
- Authorisation policy on the Gateway denies a `self` requester calling a user-scoped tool for another user, and denies write tools without a confirmation token.
- The handler-level check gives the same decisions (tested with the same cases).
- Semantic tool search is enabled; a query for "failed queries" returns `snowflake_get_failed_queries`.
- An external MCP client (for example a developer IDE assistant) can list and call tools with a valid token.

---

### CAA-161 REST API projection
**As a** developer of another system, **I want** the same tools over REST, **so that** UIs, scripts and monitoring can use them without an agent.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F7 | 3 | CAA-160 | Phase 1 subset in `api/openapi.yaml` |

**Acceptance criteria**
- The routes in `api/openapi.yaml` are served by API Gateway with a JWT authorizer and invoke the same handlers.
- For the same requester and input, REST and MCP return identical `data`.
- OpenAPI components are generated from the Pydantic models; the published spec validates.
- Throttling and per-user rate limits from `config/scopes.yaml` are applied.

---

### CAA-162 Knowledge base and search tool
**As a** consumer, **I want** answers that draw on our runbooks and access guides, **so that** instructions match how this organisation works.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F7 | 3 | CAA-010 | WF-01 |

**Acceptance criteria**
- A curated document set (access request guide, secondary roles guide, platform FAQs, onboarding pages) is stored in S3 and indexed in a Bedrock knowledge base with a scheduled sync.
- `kb_search` returns passages with title, snippet, source link and score.
- Documents have owners and a review date; changes go through pull request.
- A passage containing instruction-like text does not change agent behaviour (eval EV-303).

---

## F8 Agent and chat API

### CAA-170 Orchestrator agent
**As a** consumer, **I want** to describe my problem in my own words and get a diagnosis, **so that** I do not need to know which tool or system to ask.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F8 | 8 | CAA-151, CAA-152, CAA-160 | DX, EN, IM-12, WF via MCP |

**Acceptance criteria**
- The agent runs on AgentCore Runtime with the prompt in `prompts/system-prompt.md`, the model id from config and the Gateway as its MCP server.
- Playbooks PB-01, PB-02, PB-03, PB-07, PB-11 and PB-12 behave as described in `docs/05` section 3.
- The agent asks at most two clarifying questions and uses failed-query history to infer the table when the user does not name one.
- The agent never states an access verdict that the engine did not return in that conversation (eval gate).
- On `denied` it explains and stops; on a retryable error it retries once.
- Limits: 12 tool calls per turn, 60 s per turn.
- Conversation state is kept for the session; no entitlement data is written to long-term memory.

---

### CAA-171 Chat API with SSO and streaming
**As a** consumer, **I want** to reach the assistant through an authenticated API that streams replies, **so that** any front end can host the chat.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F8 | 5 | CAA-170 | - |

**Acceptance criteria**
- `POST /chat/sessions` and `POST /chat/sessions/{id}/messages` accept a JWT, invoke the agent with the user's identity, and stream the response.
- An unauthenticated or expired token is rejected with 401.
- The first token arrives within the NFR-01 target in `test`.
- Session history is retrievable by its owner only.
- A minimal test client (CLI or simple page) is provided for the pilot.

---

### CAA-172 Answer formatting and guardrails
**As a** consumer, **I want** answers that lead with the verdict, tell me what to do and show the evidence, **so that** I can act immediately and trust the result.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F8 | 5 | CAA-170 | - |

**Acceptance criteria**
- Diagnostic answers follow the six-part format in `docs/05` section 4; times are in the user's time zone with UTC.
- For `self` requesters, answers contain no tool names or root cause codes; for `support` and above they include codes and the diagnosis id.
- Bedrock Guardrails are configured for prompt-attack detection and PII filtering on output.
- A post-check blocks any answer asserting "should have access" without a matching engine result in the turn.
- Every `unchecked` item and relevant lag is mentioned (eval gate).
- Off-topic requests get a one-line redirect.

---

## F9 Quality, operations, launch

### CAA-180 Evaluation harness and golden set
**As a** product owner, **I want** automated evaluation of agent behaviour on every change, **so that** quality and safety cannot regress unnoticed.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F9 | 8 | CAA-170 | - |

**Acceptance criteria**
- A harness runs `evals/scenarios.yaml` against the agent with tools mocked from persona fixtures, three runs per scenario.
- Scoring covers tool selection, arguments, faithfulness, actionability, disclosure, honesty, safety and format as in `docs/09` section 4.2.
- Scenario sets reach the MVP counts in `docs/09` section 4.3.
- CI blocks merges that touch prompts, tool descriptions, engine or config when gates in `docs/09` section 4.4 fail.
- The same scenarios run as engine tests without a model.
- Results are published per run with trend.

---

### CAA-181 Observability baseline
**As an** operator, **I want** traces, metrics, dashboards and alarms, **so that** I can run the service and see what is failing across the estate.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F9 | 5 | CAA-160, CAA-170 | - |

**Acceptance criteria**
- One trace per user turn links model calls, tool calls and source calls by `trace_id`.
- Metrics in `docs/08` section 2.2 are emitted; the service health, estate insight, quality, cost and security dashboards exist.
- Alarms in `docs/08` section 2.4 are configured and routed.
- The tool audit log has a complete record for 100% of calls in a sample check.
- Logs contain canonical ids and hashes, not names or attribute values.

---

### CAA-182 Security review and go-live gate
**As a** security partner, **I want** the security acceptance criteria verified, **so that** the assistant can go to production.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F9 | 5 | CAA-172, CAA-180, CAA-181 | - |

**Acceptance criteria**
- The six criteria in `docs/07` section 9 are met and evidenced.
- Threat model reviewed with security; no open high findings.
- Credential rotation and access revocation runbooks exercised once in `test`.
- Data processing record completed with the privacy office.

---

### CAA-183 MVP pilot
**As a** product owner, **I want** a pilot with real consumers and the helpdesk, **so that** we confirm value and correctness before general release.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F9 | 3 | CAA-182 | - |

**Acceptance criteria**
- 10 to 20 pilot users and the helpdesk use the assistant for at least two weeks in production.
- Every diagnosis during the pilot is sampled or reviewed for correctness; wrong answers become eval scenarios.
- Pilot metrics (time to diagnosis, resolution without engineer, feedback score, inconclusive rate) are reported against baseline.
- A go / no-go decision for general availability is recorded.

---

# Phase 2: Depth and proactive monitoring

### CAA-201 Login failure diagnosis
**As a** consumer who cannot connect, **I want** to know why, **so that** I contact the right team with the right request.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F10 | 3 | CAA-151 | SF-09, DX-05 |

**Acceptance criteria**
- `snowflake_get_login_history` returns recent attempts with success, error, client type and auth factor; client IP only for `platform` scope.
- `diagnose_login_failure` distinguishes disabled directory account, disabled or locked Snowflake user, credential failure and network policy block, with the owner for each.
- Playbook PB-04 passes its eval scenarios.

---

### CAA-202 Change history: "it worked yesterday"
**As a** consumer whose access stopped working, **I want** to know what changed, **so that** I can get it restored quickly.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F10 | 5 | CAA-151 | ID-06, SF-10, SF-13, IM-10 |

**Acceptance criteria**
- The tools return group membership changes, last successful table access, grant changes and Immuta data source activity for a time window.
- Given a regression, the engine reports the most recent change on the access path that is later than the last success, as the probable cause.
- Actor names in change records are shown to `support` and above only.
- Playbook PB-05 passes its eval scenarios, including the recreated-table case.

---

### CAA-203 Compare two users
**As a** support engineer, **I want** to compare a user who has access with one who does not, **so that** the decisive difference is obvious.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F10 | 3 | CAA-132, CAA-151 | EN-04 |

**Acceptance criteria**
- For two users and a table, the tool returns groups, attributes, roles and subscription state that differ, and marks the differences that decide access.
- Only `support` and above may call it; a `self` requester is denied and offered a diagnosis of their own access.

---

### CAA-204 Row and masking diagnosis with policy detail
**As a** consumer, **I want** to say which accounts or columns I expected to see and be told exactly what is missing, **so that** I can request the precise entitlement.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F10 | 5 | CAA-130, CAA-131 | DX-03, DX-04, IM-09 |

**Acceptance criteria**
- `immuta_get_data_policies` returns masking and row rules with exceptions in normalised form (steward scope for full detail).
- `diagnose_row_visibility` returns missing values against the user's expectation and the attribute value or mapping row that would grant each.
- `diagnose_masked_columns` explains each named column's state and what unmasks it.
- When policy grants the expected scope and the user still sees no data, the result points to data availability, not access.

---

### CAA-205 Group details and source attributes
**As a** consumer, **I want** to know what a group is for, who owns it and how to request it, **so that** I can act on a "missing group" answer.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F10 | 2 | CAA-102 | ID-05, ID-07 |

**Acceptance criteria**
- `idp_get_group_details` returns description, owners, membership type, dynamic rule if any, and the request route.
- `idp_get_user_attributes` returns the configured ABAC attributes at the directory source, for comparison with Immuta.

---

### CAA-206 Immuta audit, subscriptions list and access requests
**As a** support engineer, **I want** Immuta audit events, a user's full subscription list and their pending requests, **so that** history and inventory questions are answered without loading the Immuta API.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F10 | 5 | CAA-110 | IM-08, IM-13, IM-14 |

**Acceptance criteria**
- Immuta audit export to S3 is enabled and queryable through Athena with partition pruning.
- `immuta_get_audit_events` returns events for a user or data source within a window.
- `immuta_list_user_data_sources` uses the option chosen in CAA-003 and returns `total` and `truncated`.
- `immuta_get_access_requests` returns pending requests and approvers.

---

### CAA-207 Warehouse, Iceberg and data product health
**As a** consumer, **I want** compute and data availability problems told apart from access problems, **so that** I do not chase the wrong fix.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F10 | 5 | CAA-123, CAA-140 | SF-11, SF-12, DP-03, DP-05, DP-06 |

**Acceptance criteria**
- `snowflake_get_warehouse_access` shows usable warehouses, state and resource-monitor suspension.
- `snowflake_get_iceberg_table_health` reports catalog integration, external volume reachability, auto-refresh state and last refresh, using the privileges agreed in ADR-007.
- Registration status and data product health come from the sources identified in CAA-004.
- Playbooks PB-08 and PB-09 pass their eval scenarios.

---

### CAA-210 Request status from ITSM and identity governance
**As a** consumer who has already requested access, **I want** to see where my request is, **so that** I do not raise it again.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F11 | 5 | CAA-151 | WF-03, WF-05 |

**Acceptance criteria**
- `ItsmPort` and `IgaPort` adapters are implemented for the organisation's tools.
- The tools return open requests with state, approver and dates.
- Playbook PB-10 combines request status with the propagation rule and gives a re-check time.

---

### CAA-211 Tickets and escalations with confirmation
**As a** consumer, **I want** the assistant to raise the ticket or escalation for me with the evidence attached, **so that** the owning team can act without asking me again.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F11 | 5 | CAA-210 | WF-04, WF-06 |

**Acceptance criteria**
- A write tool called with `dry_run: true` returns a preview and a confirmation token bound to conversation, requester and payload hash, valid 10 minutes.
- Without a valid token the action is refused by the Gateway policy and by the handler.
- The created ticket contains the verdict, root cause, evidence summary and diagnosis link, and is routed to the owner in the root cause catalog.
- Repeating the confirmed call does not create a duplicate (idempotency key).
- Eval scenarios EV-501 and EV-502 pass.

---

### CAA-212 Governance findings for over-entitlement
**As a** governance lead, **I want** to be told when someone has more access than policy intends, **so that** it is corrected and not quietly kept.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F11 | 3 | CAA-151 | WF-07 |

**Acceptance criteria**
- When actual access exceeds expected access, the engine writes a finding with evidence and notifies the governance channel, regardless of what the agent does next.
- Configured excepted roles and users do not raise findings.
- A `self` requester's answer contains no description of the excess (eval EV-019).
- Findings can be listed and resolved by governance.

---

### CAA-220 Monitoring framework and findings tools
**As a** platform owner, **I want** scheduled checks that record findings, **so that** faults are known before users report them.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F12 | 5 | CAA-160 | MN-01, MN-02 |

**Acceptance criteria**
- EventBridge Scheduler, Step Functions and a check Lambda framework run checks on configured schedules, calling existing tool handlers.
- Findings have check id, severity, subject or object, evidence, detected and resolved times, and auto-resolve when the condition clears.
- `monitor_get_platform_status` and `monitor_get_findings` return current incidents and findings.
- The agent calls platform status once at the start of a diagnostic conversation.

---

### CAA-221 Checks: integration health, failure spike, canary query
**As a** platform owner, **I want** to know within minutes when Immuta integration fails, authorisation failures spike, or a canary consumer cannot read, **so that** incidents are caught early.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F12 | 5 | CAA-220 | MC-01, MC-04, MC-07 |

**Acceptance criteria**
- MC-01 raises a major finding when any integration is not enabled or fails validation.
- MC-04 raises a finding when authorisation-class failures for a table exceed three times the 7-day baseline with at least 5 users.
- MC-07 runs a canary read on Snowflake and raises a critical finding after two consecutive failures.
- Thresholds are configuration; a noisy check can be tuned without a deploy.

---

### CAA-222 Checks: entitlement drift and orphaned access
**As a** governance lead, **I want** regular reconciliation between what Immuta intends and what the platform grants, **so that** missing and excess access are both found.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F12 | 8 | CAA-220, CAA-206 | MC-02, MC-06 |

**Acceptance criteria**
- Hourly, pairs with a subscription change in the last hour are compared (Immuta state versus platform privileges), allowing for the propagation window.
- Nightly, a full reconciliation runs from the Immuta audit export and Snowflake grant views.
- Missing grants raise `ENF-002`; excess access raises `SEC-001`; access held by disabled directory accounts raises `SEC-002`.
- A daily summary of open drift findings goes to the owning teams.

---

### CAA-223 Check: sync lag
**As an** IAM owner, **I want** the time for a group change to reach Immuta and the platform measured continuously, **so that** slow sync is visible and users get accurate wait times.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F12 | 5 | CAA-220 | MC-03 |

**Acceptance criteria**
- Lag per hop is measured by the method agreed with IAM (canary group toggle, or passive measurement from real events).
- `sync.lag_seconds` is published per hop; a finding is raised when lag exceeds the agreed threshold.
- Measured typical values update the guidance the agent gives users.

---

### CAA-224 Alert routing and estate insight dashboard
**As a** platform owner, **I want** findings routed to my team's channel and a dashboard of what is going wrong across the estate, **so that** recurring causes get fixed at the source.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F12 | 3 | CAA-221 | - |

**Acceptance criteria**
- Findings route by owner to the right channel and, for major and above, to the ITSM tool.
- The estate dashboard shows diagnoses by root cause and data product, sync lag trend and top failing tables.
- A monthly report lists the top five root causes by volume with their owners.

---

### CAA-230 Web chat UI
**As a** consumer, **I want** a web chat page, **so that** I can use the assistant from my browser.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F13 | 5 | CAA-171 | - |

**Acceptance criteria**
- SSO sign-in, streaming replies, evidence tables rendered, copy buttons on commands, feedback controls.
- Confirmation dialogs for write actions show the preview.
- Meets WCAG 2.1 AA; served through CloudFront with WAF.

---

### CAA-231 Teams or Slack bot
**As a** consumer, **I want** the assistant in the collaboration tool I already use, **so that** I do not need another site.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F13 | 5 | CAA-171 | - |

**Acceptance criteria**
- A bot in the chosen tool authenticates the user by SSO and maps them to the same identity and scopes.
- Direct messages only for diagnostics; in channels the bot declines user-specific questions.
- Monitoring alerts post to team channels.

---

### CAA-232 Feedback loop and online evaluation
**As a** product owner, **I want** user feedback and sampled automatic scoring of live conversations, **so that** quality is tracked in production.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F13 | 3 | CAA-180, CAA-230 | - |

**Acceptance criteria**
- Thumbs up/down and "this was wrong" are stored against the diagnosis id.
- 10% of conversations are scored for faithfulness and disclosure.
- A weekly review process exists; each confirmed wrong answer becomes an eval scenario before the fix ships.

---

### CAA-233 Steward view: who can see my data product
**As a** data steward, **I want** to see who can access my data product and at what level, **so that** I can review access.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F13 | 5 | CAA-206 | New steward tool (add to catalog) |

**Acceptance criteria**
- For a data product the steward owns, the tool returns counts by group and by PI and row scope, then names on request.
- A steward cannot query products they do not own.
- Privacy has approved the level of detail.

---

### CAA-234 Runbooks and support hand-over
**As an** operator, **I want** runbooks and a support model, **so that** the service can be run by the wider team.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F13 | 3 | CAA-181 | - |

**Acceptance criteria**
- Runbooks RB-01 to RB-12 in `docs/08` section 4.2 are written and each exercised once.
- On-call rota, escalation contacts and the support tiers are agreed.
- The helpdesk is trained to use the assistant with `support` scope.

---

# Phase 3: More platforms

### CAA-301 Platform adapter interface
**As a** developer, **I want** the engine to talk to platforms through one interface, **so that** adding a platform does not change engine logic.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F14 | 5 | CAA-151 | - |

**Acceptance criteria**
- A `PlatformAdapter` protocol covers user, roles, privileges, policies, table status and failed queries; the Snowflake implementation passes all existing tests unchanged in behaviour.
- Platform-specific root causes (for example SES-001) are declared by the adapter.

---

### CAA-302 Databricks tools
**As a** Databricks consumer, **I want** the same access answers for Unity Catalog, **so that** my experience matches Snowflake users'.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F14 | 8 | CAA-301 | DB-01 to DB-07 |

**Acceptance criteria**
- A service principal with the agreed read access exists (owned by the Databricks platform team).
- Each tool works against non-prod with recorded fixtures.
- Failed-query output handles masked query text when the service principal is not permitted to see it.
- The effective-permissions tool reports inherited privileges and the missing link (`USE CATALOG`, `USE SCHEMA`, `SELECT`).

---

### CAA-303 Databricks in the diagnosis engine
**As a** Databricks consumer, **I want** a table-access diagnosis, **so that** I know what to request.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F14 | 5 | CAA-302 | DX-01, DX-02 |

**Acceptance criteria**
- Seeded Databricks personas return the expected verdicts.
- Databricks-specific causes (workspace-catalog binding, compute access mode) are in the root cause catalog.
- Eval scenarios for Databricks pass the gates.

---

### CAA-304 Starburst tools and adapter
**As a** Starburst consumer, **I want** the same diagnosis, **so that** all three platforms are covered.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F14 | 8 | CAA-301 | SB-01 to SB-04 |

**Acceptance criteria**
- Tools work against the Starburst non-prod cluster with fixtures; the query history source is confirmed.
- The adapter treats Immuta's decision as the enforcement decision where the Immuta plugin is the access control, and checks catalog visibility separately.
- Seeded personas and eval scenarios pass.

---

### CAA-305 Producer storage tools and Iceberg staleness check
**As a** platform engineer, **I want** to see the producer's Glue and Iceberg state and whether the consumer platform can read the storage, **so that** data availability faults are pinned down.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F14 | 5 | CAA-207 | AW-01 to AW-03, MC-05 |

**Acceptance criteria**
- A cross-account read role exists in producer accounts for Glue and metadata objects.
- The tools return Glue table details, the current Iceberg snapshot and a storage access evaluation with the denying statement if any.
- MC-05 raises a finding when the platform's snapshot lags the producer beyond the freshness SLA.
- Tools are limited to `platform` scope.

---

### CAA-306 Platform specialist sub-agents
**As a** consumer, **I want** deep platform-specific follow-up answers, **so that** unusual cases are handled well.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F14 | 5 | CAA-303, CAA-304 | - |

**Acceptance criteria**
- Specialists for Snowflake, Databricks and Starburst are available to the orchestrator as tools, each with only its platform's granular tools.
- Verdicts still come only from the engine.
- Tool-selection accuracy on the eval set is at or above the single-agent baseline; latency increase is within an agreed budget.

---

### CAA-307 Access snapshots, diff over time and remaining tools
**As a** support engineer, **I want** to see how a user's access changed between two dates, **so that** long-running issues can be traced.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F14 | 5 | CAA-222 | EN-05, IM-15, SF-14 |

**Acceptance criteria**
- Daily access snapshots are written to S3 in Parquet and queryable by date.
- `entitlement_diff_over_time` returns added, removed and changed entitlements between two dates.
- Projects and purposes, and authentication policies, are available as tools.

---

### CAA-308 Decision and build: on-behalf-of probe
**As a** consumer, **I want** the assistant to confirm my effective access when metadata is lagged, **so that** I get a definite answer.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F14 | 3 | CAA-151 | SF-15 |

**Acceptance criteria**
- Security decides whether the probe is permitted; the decision updates ADR-005. Immuta's Agentic Access API is assessed as an option.
- If approved: the probe runs a count only, as the user, for `self` only, and is audited; it is off by default per environment.
- If not approved: the story closes with the decision recorded.

---

# Phase 4: Consumer onboarding

### CAA-401 Onboarding prerequisites
**As a** new consumer, **I want** an ordered list of everything I need for a data product on my chosen platform, **so that** I can start without asking around.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F15 | 5 | CAA-140 | OB-01 |

**Acceptance criteria**
- Prerequisite templates exist per platform and merge with the data product's access contract.
- Each step has a title, a reason, a request route, an indicative lead time supplied by the owning team, and a verifier.
- Platform owners have reviewed their templates.

---

### CAA-402 Live onboarding checklist
**As a** new consumer, **I want** to see which steps I have completed and what is next, **so that** I always know where I am.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F15 | 5 | CAA-401, CAA-210 | OB-02 |

**Acceptance criteria**
- Each step's state (`done`, `pending`, `blocked`) is computed by its verifier tool, not self-reported.
- Pending steps show the request and who must act.
- The consumer can opt in to a notification when a pending step completes.

---

### CAA-403 Sample code and connection profiles
**As a** new consumer, **I want** working starter code in my language for my platform, **so that** my first query succeeds.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F15 | 8 | CAA-401 | OB-03, OB-04 |

**Acceptance criteria**
- Reviewed templates exist for the launch set in `docs/11` section 3; security has approved each connection pattern.
- Generated code contains no secrets, sets session context correctly (for example secondary roles on Snowflake), and selects named columns with a limit.
- The accompanying note tells the consumer which columns will be masked and what row scope to expect, from their own entitlements.
- Every template is executed in CI against a seeded persona.
- Connection profiles per platform and environment are maintained by the platform teams.

---

### CAA-404 Guided access requests
**As a** new consumer, **I want** the assistant to raise the outstanding requests for me, **so that** I do not have to find each form.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F15 | 5 | CAA-402, CAA-211 | OB-05 |

**Acceptance criteria**
- With one confirmed preview, the assistant submits the group, attribute and subscription requests that are outstanding.
- Requests already in progress are not duplicated.
- The same confirmation-token control as other write tools applies.

---

### CAA-405 Onboarding conversation and evals
**As a** new consumer, **I want** to state my goal and be guided to a first successful query, **so that** onboarding is one conversation, resumable over days.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F15 | 5 | CAA-402, CAA-403 | - |

**Acceptance criteria**
- The assistant goes from goal to data product, platform choice, checklist, requests, connection and sample code.
- The journey resumes across sessions using stored preferences (product, platform, language), not stored entitlements.
- A failed first query hands over to the diagnostic playbooks.
- An onboarding eval set passes agreed gates.

---

### CAA-406 Onboarding measures
**As a** product owner, **I want** onboarding outcomes measured, **so that** slow steps are improved.

| Feature | Pts | Depends | Tools |
|---|---|---|---|
| F15 | 2 | CAA-405 | - |

**Acceptance criteria**
- Time from first question to first successful query, first-query success rate and most-blocked steps are reported per data product and owning team.
