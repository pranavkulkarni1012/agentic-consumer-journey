# 12 - Assumptions and Open Questions

This design was written from a short description of the platform. Everything below was assumed and should be confirmed. **Blocking** items must be answered before the stories that depend on them start.

## 1. Assumptions

| # | Assumption | If wrong |
|---|---|---|
| A1 | Entra ID (Azure AD) is reachable through Microsoft Graph and holds the AD groups used by Immuta policies (synced from on-prem AD if applicable) | Swap the Graph connector for an LDAP adapter behind the same port; ID-06 changes source |
| A2 | Immuta gets groups and attributes from the identity provider (SCIM, SAML/OIDC claims or an external user info endpoint) | The L1 comparison (directory versus Immuta) changes which side is authoritative for attributes |
| A3 | The Immuta Snowflake integration uses table grants (one Immuta-managed role per user) with secondary roles | SF-02/SF-03 logic and SES-001 change if access is granted another way |
| A4 | Row-level security is by account, driven by a user attribute or an entitlement mapping table | Add another RLS model type in `config/rls-models.yaml` |
| A5 | PI columns are identified by Immuta tags and protected by masking policies with group or attribute exceptions | EN-02 needs a different source for "what is PI" |
| A6 | A data product catalog and a telemetry store exist and can be queried | DP tools fall back to config files and Snowflake grants |
| A7 | AWS is the hosting cloud, and Amazon Bedrock with AgentCore is permitted for confidential internal metadata | See ADR-001 fallback (self-hosted agent on ECS/Lambda with the same tools) |
| A8 | Snowflake is Enterprise Edition or higher (needed for `ACCESS_HISTORY`, row access and masking policies) | SF-06/SF-10 lose object-level evidence |
| A9 | Consumers and Snowflake users map one to one, with the Snowflake login derived from the UPN or email | Identity resolution needs an explicit mapping table |
| A10 | The assistant is internal-only, for employees with SSO | External consumers would need a separate identity design |
| A11 | Read-only diagnosis is acceptable for v1; no automated remediation | Scope and risk review change substantially |
| A12 | ITSM and identity governance tools have APIs | Phase 2 actions become deep links instead of API calls |
| A13 | English-language chat | Add language handling and translated KB content |

## 2. Open questions

### Platform and identity

| # | Question | Needed for | Blocking |
|---|---|---|---|
| Q1 | Is AD on-prem with Entra sync, Entra-only, or another IdP? How do groups and attributes reach Immuta, and how often? | ID tools, sync windows | **Yes** (CAA-102) |
| Q2 | Which attributes drive policies, and where is each mastered (directory, Immuta, external endpoint)? | IM-02, EN-01, config | **Yes** (CAA-110) |
| Q3 | Group naming conventions for data-mesh groups (prefixes)? | ID-03 filter | **Yes** (CAA-102) |
| Q4 | How is the Snowflake user name related to the UPN? Any exceptions? | ID-01 | **Yes** (CAA-101) |
| Q5 | Immuta deployment: SaaS or self-managed, version, which integrations and features (table grants, low row access policy mode, impersonation)? | All IM tools | **Yes** (CAA-003) |
| Q6 | Immuta role prefix for per-user Snowflake roles; name of the Immuta database in Snowflake | SF-02, SF-07 | **Yes** (CAA-120) |
| Q7 | Are there excepted roles or users that bypass Immuta policies? How should the assistant treat them? | Engine (SEC-001 false positives) | Yes (CAA-150) |
| Q8 | Does the platform use Snowflake database roles or future grants for data-mesh objects? | SF-03 | Yes (CAA-121) |

### Data mesh specifics

| # | Question | Needed for | Blocking |
|---|---|---|---|
| Q9 | What is "telemetry" today: which store, schema, freshness, and who owns it? | DP-04, DP-05 | **Yes** (CAA-141) |
| Q10 | Is there a data product catalog or registration service with an API? Does it hold access requirements? | DP-01, DP-02, DP-03 | **Yes** (CAA-140) |
| Q11 | How are tables registered on Snowflake: externally managed Iceberg tables (Glue catalog integration), external tables, or both? Auto-refresh? | SF-08, SF-11 | No (Phase 2) |
| Q12 | Exact RLS implementation per domain: attribute comparison or lookup table? Which attribute or table? | EN-01 | **Yes** (CAA-130) |
| Q13 | PI classification scheme: tag names, categories, who may be unmasked and how it is requested | EN-02 | **Yes** (CAA-131) |
| Q14 | One Snowflake account or several? Same question for Databricks workspaces and Starburst clusters | Connectors, config | Yes (CAA-120) |

### Hosting, security, operations

| # | Question | Needed for | Blocking |
|---|---|---|---|
| Q15 | Approved AWS Region(s); is Bedrock AgentCore approved; which Claude models are enabled? | ADR-001 | **Yes** (CAA-002) |
| Q16 | Is there an existing agent or agent platform these tools should plug into first? | Scope of CAA-170 | Yes |
| Q17 | Network path to Immuta, Snowflake, Databricks, Graph from the workload VPC (PrivateLink, proxy, NAT allow-list)? | CAA-010 | **Yes** |
| Q18 | Will platform owners grant the read permissions listed in [07 section 4](07-security-and-governance.md)? Especially Immuta `GOVERNANCE` and Entra `AuditLog.Read.All` | CAA-007 | **Yes** |
| Q19 | Who may see other users' access (support, stewards, managers)? Privacy office position? | Scopes | Yes (CAA-008) |
| Q20 | Chat channel preference: web, Teams, Slack, or inside an existing portal? | Phase 2 UI | No |
| Q21 | ITSM and identity governance products and their APIs | Phase 2 | No |
| Q22 | Retention requirements for transcripts and diagnosis records | Data stores | No |
| Q23 | IaC and CI/CD standards (CDK or Terraform; GitHub Actions or CodePipeline) | CAA-001 | Yes |
| Q24 | Expected volumes: users, access tickets per month, peak concurrency | NFRs, cost | No (CAA-005) |
| Q25 | Is a canary identity with a toggled AD group acceptable to IAM for sync-lag monitoring? | MC-03 | No (Phase 2) |
| Q26 | Databricks is run by another team: who owns the service principal request and system table access? | Phase 3 | No, but start early |

## 3. Facts to verify in spike CAA-003

Each becomes a recorded fixture or a corrected SQL file.

| # | Verify | Where used |
|---|---|---|
| V1 | Immuta: `GET /bim/user` filters and the aggregated user object fields (`authorizations`, `bimAuthorizations`, `iamAuthorizations`, `externalUserIds`) | IM-01, IM-02 |
| V2 | Immuta: shape of `subscriptionPolicy` and global policy definitions; which policy endpoints are available in your version | IM-06, IM-09 |
| V3 | Immuta: `GET /dataSource/{id}/access` filtering by user, and state values | IM-05 |
| V4 | Immuta: `policyInfo` and `visibilityReport` response for attribute-based and lookup-based row policies | IM-07, EN-01 |
| V5 | Immuta: column tag retrieval (data dictionary endpoint) | IM-11 |
| V6 | Immuta: minimum permission set for the service user | Security |
| V7 | Immuta: `GET /integrations/{id}/status` values | IM-12 |
| V8 | Immuta: UAM export schema in S3 and event types for subscription and policy changes | IM-08, IM-14, MC-02 |
| V9 | Snowflake: each SQL file runs under `CAA_DIAG_READER` with database roles only; note any view needing more | All SF |
| V10 | Snowflake: `GRANTS_TO_ROLES.GRANTED_ON` values for Iceberg and external tables; database-role grants | SF-03, SF-04 |
| V11 | Snowflake: `QUERY_HISTORY.EXECUTION_STATUS` values and `SECONDARY_ROLE_STATS` JSON shape | SF-05 |
| V12 | Snowflake: `ACCOUNT_USAGE.TABLES.IS_ICEBERG` availability; Iceberg status functions and required privileges | SF-08, SF-11 |
| V13 | Snowflake: observed latency of each view in your account | ADR-007, sync windows |
| V14 | Snowflake: real error codes and messages for the top 20 failure types in the last 30 days | Error catalog |
| V15 | Graph: `transitiveMemberOf` paging and `checkMemberGroups` limits in your tenant; audit log retention | ID tools |
| V16 | AgentCore: Gateway Lambda target tool schema format; how requester context reaches the Lambda; Cedar context attributes for tool input | CAA-160 |
| V17 | Case sensitivity of user ids, group names and attribute values in Immuta matching | ID-01, IM-16 |

## 4. Risks

| # | Risk | Likelihood | Impact | Response |
|---|---|---|---|---|
| R1 | Policy shapes are too varied to normalise | Medium | High | Start with the 3 to 5 most common global policies; return `unknown` for the rest; expand by volume |
| R2 | Read permissions not granted by source owners | Medium | High | Engage owners in Phase 0 with the least-privilege list; offer audit of the service identity |
| R3 | `ACCOUNT_USAGE` lag makes fresh failures invisible | High | Medium | ADR-007 live paths; ask for query id; state the lag |
| R4 | Wrong "you should have access" answer | Low | High | Engine-only verdicts; eval gate at zero; `unknown` by default |
| R5 | Catalog or telemetry not usable | Medium | Medium | Config-file fallback; Snowflake grants as inventory |
| R6 | Agent platform features change or are not available in Region | Medium | Medium | Tools are plain Lambda + MCP; agent host is replaceable (ADR-001) |
| R7 | Entitlement disclosure incident | Low | High | Three enforcement points; evals; audit; pen test |
| R8 | Low adoption (users still raise tickets) | Medium | Medium | Put the assistant in the ticket form flow; helpdesk uses it first |
| R9 | Cost of model and Snowflake queries higher than expected | Medium | Low | Composite tools, caching, budgets, smaller model for utilities |
| R10 | Second-team dependency for Databricks delays Phase 3 | High | Low (for MVP) | Start requests during Phase 1 |
