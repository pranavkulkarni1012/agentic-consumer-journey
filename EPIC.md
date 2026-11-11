# EPIC: Consumer Access Assistant

| Field | Value |
|---|---|
| **Epic key** | `CAA` (replace with the tracker's key) |
| **Epic name** | Consumer Access Assistant: agentic access diagnostics for the data mesh |
| **Programme** | Agentic Consumer Journey |
| **Owner** | Data platform engineering |
| **Status** | Proposed |
| **Version** | 1.0 (2026-11-10) |
| **Design docs** | [`docs/`](docs/01-solution-overview.md) |
| **Stories** | [`STORIES.md`](STORIES.md) |

## 1. Summary

Build a chat assistant and a reusable library of read-only diagnostic tools that tell a data consumer why they can or cannot reach a data product, whether they are supposed to, and exactly what to do next. The assistant gathers evidence from Entra ID / AD, Immuta, Snowflake (then Databricks and Starburst), platform telemetry and the data product catalog, and compares the access a user is *expected* to have with the access they *actually* have. The same tools power scheduled monitoring that finds sync faults before users report them, and later a guided consumer onboarding journey.

## 2. Problem statement

Access to a data product depends on a chain of six links: the person's identity, their directory groups and attributes, Immuta policy, platform grants, session context, and the registered table itself. When a link breaks, consumers get a generic error, zero rows or masked values. Finding the broken link takes a platform engineer checking each system by hand. Tickets are slow, get routed to the wrong team, and the answer to "should this user have access" depends on who is asked.

## 3. Business value

| Value | How |
|---|---|
| Faster time to data for consumers | Self-service diagnosis in minutes |
| Platform engineering capacity returned | Fewer access tickets needing a specialist; escalations arrive with evidence |
| Stronger governance | Consistent, policy-based answers; over-entitlement found and reported; no pressure to over-grant to close a ticket |
| Earlier fault detection | Sync and enforcement faults detected by monitoring |
| Reusable capability | Tools exposed over MCP and REST for other agents, UIs and automation |
| Foundation for onboarding | The same tools verify onboarding prerequisites |

## 4. Objectives and key results

| Objective | Key result | Target |
|---|---|---|
| O1 Consumers resolve access issues themselves | Access tickets resolved without a platform engineer | 60% or more, 6 months after MVP |
| | Median time to diagnosis in chat | Under 2 minutes |
| O2 Diagnoses are trustworthy | Correct root cause on the golden scenario set | 95% or more |
| | Wrong "you should have access" answers | Zero in evals; every production case reviewed |
| O3 Faults are found early | Sync faults detected before the first user report | 70% or more |
| O4 Tickets go to the right team first time | Mis-routed access tickets | Halved against baseline |
| O5 The capability is reusable | Tools consumed by at least one other agent or client | 1 or more by end of Phase 2 |

Baselines are captured in story CAA-005.

## 5. Scope

### In scope

- Diagnostic tools for identity, directory entitlements, Immuta, Snowflake, row-level security and PI access (Phase 1).
- A deterministic diagnosis engine that produces expected-versus-actual verdicts with root causes and evidence.
- A conversational agent with playbooks, hosted on AWS.
- MCP and REST exposure of every tool.
- Proactive monitoring of integration health, entitlement drift, sync lag and failure spikes (Phase 2).
- Ticket and escalation creation with user confirmation (Phase 2).
- Web and collaboration-tool chat channels (Phase 2).
- Databricks, Starburst and producer storage coverage (Phase 3).
- Consumer onboarding: prerequisites, live checklist, sample code, guided requests (Phase 4).

### Out of scope

- Granting, revoking or changing access, policies, groups or attributes.
- Reading business data from data products.
- Replacing Immuta, the identity governance tool or the ITSM tool.
- Producer onboarding (noted as a later idea).
- Automated remediation.

## 6. Users and stakeholders

| Role | Interest |
|---|---|
| Data consumers | Primary users |
| Platform helpdesk / support | Users with wider scope; first escalation tier |
| Data stewards, data product owners | Policy outcomes for their products |
| Snowflake, Immuta, IAM, Databricks, Starburst platform owners | Grant read access to the service identities; receive escalations and findings |
| Data governance, security, privacy | Scope model, data handling, over-entitlement findings |
| Cloud platform / architecture | Hosting, Region, agent platform approval |

Fill in names for product owner, engineering lead, architect, security partner and each platform owner in the tracker.

## 7. Features and phases

| Phase | Feature | Outcome | Stories |
|---|---|---|---|
| **0 Foundations** | F0 Platform readiness | Decisions confirmed, service identities, skeleton deployed, API facts verified | CAA-001 to CAA-010 |
| **1 MVP** | F1 Identity and directory tools | Who the user is everywhere; their groups | CAA-101, 102 |
| | F2 Immuta tools | Entitlements, subscription, policy, per-user policy outcome | CAA-110 to 114 |
| | F3 Snowflake tools | Roles, grants, failed queries, policies, table status | CAA-120 to 123 |
| | F4 Entitlement answers | Row visibility, PI access, access summary | CAA-130 to 132 |
| | F5 Catalog and telemetry | Data product and access inventory | CAA-140, 141 |
| | F6 Diagnosis engine | Expected versus actual verdict with root causes | CAA-150 to 152 |
| | F7 Tool platform | MCP Gateway, authorisation policy, REST API, knowledge base | CAA-160 to 162 |
| | F8 Agent and chat API | Conversational diagnosis | CAA-170 to 172 |
| | F9 Quality, operations, launch | Evals, observability, security review, pilot | CAA-180 to 183 |
| **2 Depth and monitoring** | F10 Deeper diagnostics | Logins, change history, comparisons, masking and row diagnosis, health | CAA-201 to 207 |
| | F11 Workflow | Request status, tickets, escalations, governance findings | CAA-210 to 212 |
| | F12 Proactive monitoring | Scheduled checks, findings, alerts, estate dashboard | CAA-220 to 224 |
| | F13 Channels and feedback | Web UI, Teams/Slack, feedback loop, steward view, runbooks | CAA-230 to 234 |
| **3 More platforms** | F14 Databricks, Starburst, storage | Same experience on all platforms | CAA-301 to 308 |
| **4 Onboarding** | F15 Consumer onboarding | Guided path from discovery to first query | CAA-401 to 406 |

Indicative size: Phase 0 about 2 sprints; Phase 1 about 5 to 6 sprints for a team of 3 to 4 engineers; later phases to be estimated after MVP. These are planning guesses, not commitments; re-estimate after spike CAA-003.

## 8. Epic acceptance criteria

The epic's MVP (Phases 0 and 1) is accepted when:

1. A consumer can ask in natural language why they cannot access a named Snowflake table and receive a verdict, the root cause, the next action and an evidence table.
2. For each seeded persona in `docs/09` the assistant returns the expected verdict and root cause.
3. The assistant answers "which accounts can I see" and "what PI access do I have" for a table from policy and entitlements, without reading data.
4. The assistant returns the user's last 10 failed queries from the last 5 days with a cause class for each.
5. A `self` user cannot obtain another user's access information by any phrasing; a `support` user can.
6. Every tool is callable over MCP and over REST with the same result and the same authorisation.
7. No tool can modify any source system; service identities hold read privileges only, verified by each platform owner.
8. Every answer cites evidence with source and freshness, and states what could not be checked.
9. Eval gates in `docs/09` are met in CI; security acceptance criteria in `docs/07` are met.
10. Dashboards, alarms and audit records exist as specified in `docs/08`.

Later phases have their own acceptance criteria in the stories.

## 9. Non-functional requirements (summary)

| Area | Requirement |
|---|---|
| Performance | First token p95 under 6 s; full diagnosis p95 under 45 s |
| Availability | 99.5% in business hours; degrades gracefully when a source is down |
| Correctness | 95% or more on golden scenarios; zero false "expected yes" |
| Security | Authorisation outside the model at three points; read-only; no business data |
| Auditability | 100% of tool calls and diagnoses recorded for 400 days |
| Freshness | Lagged data always labelled |

Full list: [`docs/08-nfr-observability-operations.md`](docs/08-nfr-observability-operations.md).

## 10. Dependencies

| Dependency | Owner | Needed by |
|---|---|---|
| Approval to use Amazon Bedrock and AgentCore in an approved Region | Cloud platform, security | Phase 0 |
| Read-only service identity in Snowflake | Snowflake platform | Phase 0 |
| Service user and permissions in Immuta; audit export to S3 | Immuta admin | Phase 0 (export by Phase 2) |
| App registration with Graph read permissions | IAM | Phase 0 |
| Network paths to each source | Network, cloud platform | Phase 0 |
| Non-prod tenants and seeded personas | Each platform owner | Phase 0 |
| Access to the data product catalog and telemetry | Mesh platform | Phase 1 |
| Scope model sign-off | Security, privacy | Phase 1 |
| ITSM and identity governance API access | Service management, IAM | Phase 2 |
| Databricks service principal and system table access | Databricks platform team | Phase 3 (request in Phase 1) |
| Starburst service account | Starburst platform | Phase 3 |
| Connection profiles and reviewed code templates | Platform teams, security | Phase 4 |

## 11. Assumptions

Thirteen assumptions are listed in [`docs/12-assumptions-and-open-questions.md`](docs/12-assumptions-and-open-questions.md). The ones that most affect scope: Entra ID is reachable through Microsoft Graph; Immuta's Snowflake integration uses per-user roles with table grants; row-level security is by account through an attribute or a mapping table; a catalog and telemetry store exist.

## 12. Risks

| Risk | Response |
|---|---|
| Policy shapes too varied to evaluate deterministically | Cover the common policies first; return "unknown" for the rest; expand by volume |
| Source owners decline read permissions | Engage in Phase 0 with a least-privilege list and activity monitoring |
| Metadata lag hides fresh failures | Label freshness; lag rule; selective live paths (ADR-007) |
| A wrong "should have access" answer | Engine-only verdicts; zero-tolerance eval gate |
| Entitlement disclosure | Three enforcement points; security evals; pen test |
| Agent platform changes or is unavailable | Thin agent; tools are plain Lambda and MCP; documented fallback (ADR-001) |
| Low adoption | Embed in the ticket flow; helpdesk uses it first |

Full register: `docs/12`, section 4.

## 13. Milestones

| Milestone | Exit criteria |
|---|---|
| M0 Ready to build | Blocking open questions answered; API facts verified; service identities issued; skeleton deployed |
| M1 Engine demo | `diagnose_table_access` returns correct verdicts for all seeded personas from a CLI, no agent involved |
| M2 Agent alpha | Conversational diagnosis in `dev`; eval gates green |
| M3 MVP pilot | 10 to 20 pilot users in production; security criteria met |
| M4 MVP general availability | Pilot feedback addressed; support model live |
| M5 Monitoring live | Phase 2 checks running; findings routed |
| M6 Multi-platform | Databricks and Starburst parity |
| M7 Onboarding | Guided onboarding for a first set of data products |

## 14. Definition of done (epic)

- All MVP stories closed with acceptance criteria demonstrated.
- Epic acceptance criteria 1 to 10 verified in production with pilot users.
- Documentation current: tool catalog, specifications, runbooks, ADRs accepted.
- Operational ownership handed over with on-call, dashboards and alarms.
- Benefits tracking in place against the baselines from CAA-005.
