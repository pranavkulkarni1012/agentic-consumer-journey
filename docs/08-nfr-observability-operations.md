# 08 - Non-functional Requirements, Observability and Operations

## 1. Non-functional requirements

Targets are proposals to be confirmed with the product owner once baseline volumes are known (CAA-005).

| ID | Area | Requirement | Target | How measured |
|---|---|---|---|---|
| NFR-01 | Latency | Time to first streamed token | p50 under 3 s, p95 under 6 s | BFF metric |
| NFR-02 | Latency | Full diagnostic answer (PB-01) | p50 under 20 s, p95 under 45 s | Trace duration |
| NFR-03 | Latency | Single granular tool | p95 under 5 s (Snowflake cold warehouse excluded: under 12 s) | Tool metric |
| NFR-04 | Latency | `diagnose_table_access` | p95 under 15 s | Tool metric |
| NFR-05 | Availability | Chat API | 99.5% in business hours across user regions | Synthetic probe |
| NFR-06 | Degradation | One source system down | Assistant still answers, marks the layer unchecked | Chaos test |
| NFR-07 | Correctness | Root cause on golden set | 95% or more; zero false "expected yes" | Eval suite in CI |
| NFR-08 | Capacity | Concurrent conversations | 50 at launch, scale to 500 without redesign | Load test |
| NFR-09 | Freshness | Every lagged answer states `data_as_of` | 100% | Contract test |
| NFR-10 | Security | Scope enforcement | 100% on bypass eval set | Eval suite |
| NFR-11 | Cost | Cost per resolved conversation | Tracked from day one; target set after one month | Cost dashboard |
| NFR-12 | Auditability | Tool calls with complete audit record | 100% | Log completeness check |
| NFR-13 | Source load | Snowflake credits for diagnostics | Budget alarm; XS warehouse only | Resource monitor |
| NFR-14 | Source load | Immuta API calls | Under an agreed rate; backoff on 429 | Connector metric |
| NFR-15 | Maintainability | New tool end to end | Under 2 days following [04 section 6](04-tool-specifications.md) | Team measure |
| NFR-16 | Portability | Tools usable by another MCP client | Demonstrated with one external client | Integration test |
| NFR-17 | Recoverability | Stateless compute; state in DynamoDB/S3 | RPO 24 h, RTO 4 h for the assistant | DR test |
| NFR-18 | Accessibility | Web chat UI | WCAG 2.1 AA | Audit |

## 2. Observability

### 2.1 Signals

| Signal | Tooling | Content |
|---|---|---|
| Traces | OpenTelemetry via AgentCore Observability to CloudWatch | One trace per user turn: model calls, tool calls, source calls, with `trace_id` in every tool envelope |
| Metrics | CloudWatch embedded metric format | See 2.2 |
| Logs | CloudWatch Logs, JSON | Tool audit log, engine decisions, connector errors |
| Model I/O | Restricted log group | Prompts and completions for evaluation |
| Quality | AgentCore Evaluations and the offline eval suite | Scenario pass rates, online sampling |

### 2.2 Metrics

| Metric | Dimensions | Use |
|---|---|---|
| `tool.invocations`, `tool.errors`, `tool.latency_ms` | tool, status, platform | Tool health |
| `source.calls`, `source.errors`, `source.latency_ms`, `source.throttles` | system, operation | Upstream health |
| `diagnosis.count` | verdict, top root cause, platform | What is going wrong in the estate |
| `diagnosis.unchecked_layers` | layer | Evidence gaps |
| `agent.turn_latency_ms`, `agent.tool_calls_per_turn`, `agent.tokens_in/out` | model | Performance and cost |
| `authz.denied` | tool, scope | Security |
| `conversation.resolved` | by_user_action, by_escalation, abandoned | Outcome |
| `feedback.score` | thumbs up/down | Quality |
| `monitor.findings_open` | check, severity | Proactive monitoring |
| `sync.lag_seconds` | hop (directory→immuta, immuta→platform), platform | Sync SLO |

### 2.3 Dashboards

1. **Service health**: availability, latency percentiles, error rates per tool and source.
2. **Estate insight**: diagnoses by root cause and data product, trend of sync lag, top failing tables. This is a product in itself for platform owners.
3. **Quality**: eval pass rate per release, feedback score, `inconclusive` rate.
4. **Cost**: tokens, Snowflake credits, Lambda, per conversation.
5. **Security**: denied calls, unusual `support` usage, write actions.

### 2.4 Alarms

| Alarm | Condition | Severity | Route |
|---|---|---|---|
| Chat API availability | Synthetic probe fails 3 of 5 | High | On-call |
| Tool error rate | Over 10% for 10 min, any tool | Medium | On-call |
| Source auth failure | Any `UPSTREAM_AUTH` | High | On-call + source owner |
| Inconclusive rate | Over 20% for 1 h | Medium | Team channel |
| Eval regression | Pass rate drops below gate in CI | Blocks deploy | Pipeline |
| Scope denials | Over 20 from one requester in 10 min | Medium | Security |
| Snowflake credit budget | Resource monitor at 80% | Medium | Team channel |
| Immuta non-GET by `svc-caa` (MC-08) | Any | High | Security |

## 3. Proactive monitoring checks

Findings have `severity` (`info`, `minor`, `major`, `critical`), a `subject` or `object`, evidence, and auto-resolve when the condition clears.

| Check | Method | Default threshold | Finding |
|---|---|---|---|
| MC-01 Integration health | IM-12 every 5 min | Any integration not enabled or failing validation | `PLT-001`, major |
| MC-02 Entitlement drift | For (user, data source) pairs with a subscription change in the last hour: IM-05 versus SF-03. Nightly: full reconciliation from the Immuta audit export and `GRANTS_TO_ROLES` in Athena/Snowflake | Mismatch older than the propagation window | `ENF-002` or `SEC-001`, major |
| MC-03 Sync lag | Canary identity: toggle membership of a canary AD group on a schedule, time its arrival in Immuta and the canary grant in Snowflake | Over 60 min directory→Immuta, over 15 min Immuta→platform (confirm with owners) | `PLT-002`, major |
| MC-04 Failure spike | Count authorisation-class failures per table per 15 min against a 7-day baseline | 3x baseline and at least 5 users | `PLT-003` candidate, minor→major |
| MC-05 Iceberg staleness | Producer snapshot (AW-02) versus platform view (SF-11) | Behind by more than the data product's freshness SLA | `DAT-003`, minor |
| MC-06 Orphaned access | Platform users with grants whose directory account is disabled | Any | `SEC-002`, major |
| MC-07 Canary query | Canary service user reads a canary table on each platform | Failure twice in a row | `PLT-003`, critical |
| MC-08 Service identity misuse | Immuta audit for non-GET by `svc-caa`; Snowflake queries by `CAA_DIAG_SVC` without the CAA query tag | Any | Security, critical |

MC-03 needs write access to one canary AD group through a separate, tightly scoped identity owned by IAM. If IAM does not accept that, measure lag passively from real events (group change time in ID-06 versus first appearance in IM-02).

## 4. Operations

### 4.1 Ownership

| Thing | Owner |
|---|---|
| Assistant service, tools, engine | Data platform engineering (this team) |
| Config: scopes, group prefixes, RLS models, PI classification | This team, with CODEOWNERS from governance |
| Knowledge base content | Platform teams, per document |
| Service identities | Each source system's owner |
| Findings triage | Owning team per `Owner` column in the root cause catalog |

### 4.2 Runbook index

To be written during build (story CAA-234). Each runbook: symptoms, checks, fix, rollback, contacts.

| ID | Runbook |
|---|---|
| RB-01 | Source credential rejected or expired (per system) |
| RB-02 | Rotate a service credential |
| RB-03 | Revoke the assistant's access to a source in under 15 minutes |
| RB-04 | Source system down: confirm degraded mode, post banner |
| RB-05 | Wrong diagnosis reported: capture, add to eval set, fix, back-test |
| RB-06 | Suspected disclosure: contain, audit trail extraction, notify security |
| RB-07 | Snowflake diagnostics warehouse over budget |
| RB-08 | Immuta API throttling |
| RB-09 | Model or Region outage: switch model id / fail to "tools only" REST mode |
| RB-10 | Update the error catalog or root cause catalog |
| RB-11 | Add a data product's RLS model or access contract |
| RB-12 | Monitoring check is noisy: tune threshold, suppress, review |

### 4.3 Release and change

- Trunk-based development, protected `main`, CODEOWNERS on `config/`, `prompts/`, `infra/`.
- Pipeline gates: unit and contract tests, static analysis, secret scan, IaC diff, deploy to `dev`, eval suite, manual approval to `prod`.
- Prompt, tool description and config changes are code changes and run the full eval suite.
- Feature flags per tool and per platform (`NOT_ENABLED` when off).
- Rollback: redeploy the previous version; the agent runtime, Lambda and config are versioned together.

### 4.4 Feedback loop

1. Thumbs up/down and "this was wrong" in chat, linked to the diagnosis id.
2. Weekly review of down-votes, `inconclusive` verdicts and escalations that bounced.
3. Each confirmed wrong answer becomes an eval scenario before the fix ships.
4. Monthly: top root causes by volume go to the owning teams as improvement candidates. If `SES-001` dominates, the better fix is default secondary roles, not more diagnoses.

### 4.5 Support model

| Tier | Who | Handles |
|---|---|---|
| 0 | The assistant | Self-service diagnosis |
| 1 | Platform helpdesk using the assistant with `support` scope | Cases the user could not resolve |
| 2 | Owning platform team | Escalations with evidence pack |
| 3 | This team | Assistant defects, wrong diagnoses |
