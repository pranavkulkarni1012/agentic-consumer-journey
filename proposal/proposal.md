# Proposal: Consumer Access Assistant

| | |
|---|---|
| **Prepared for** | Senior management, product owner, architecture review |
| **Prepared by** | Data platform engineering |
| **Date** | November 2026 |
| **Status** | Design complete. Nothing is built yet. |
| **Decision requested** | Approve Phase 0 (foundations) and Phase 1 (MVP) |
| **Slides** | [`presentation.pptx`](presentation.pptx), [`presentation.html`](presentation.html) |

## 1. Summary

When a data consumer cannot see data they expect to see, finding the reason takes a platform engineer checking several systems by hand. We propose a chat assistant that does this check automatically, tells the consumer whether they are supposed to have access, and gives them the one next step.

The assistant is read-only. It does not grant access and does not read the contents of data products. The decision about whether someone should have access is made by tested code that compares policy with what the platform has actually granted, and the AI model only explains the result.

We are asking for approval to run a foundations phase and build the MVP for Snowflake, Immuta and Entra ID.

## 2. Problem

A consumer can read a table on the data mesh only when six things are all true:

| # | Link | Where it lives |
|---|---|---|
| 1 | **Identity**: the same, enabled person in every system | AD / Entra ID, Immuta, the data platform |
| 2 | **Entitlements**: the right AD groups and user attributes | AD / Entra ID, synced to Immuta |
| 3 | **Policy**: Immuta subscribes them, and decides which rows and columns they see | Immuta |
| 4 | **Platform grants**: the matching role and grants exist | Snowflake, Databricks, Starburst |
| 5 | **Session**: the query runs with the right role and warehouse | The consumer's own session |
| 6 | **Data**: the table is registered and current | Producer storage and the platform |

When one link breaks, the consumer sees a generic error ("object does not exist or not authorized"), zero rows, or masked values. Nothing tells them which link it was. The effects:

- **Slow.** An engineer checks each system by hand for every ticket.
- **Mis-routed.** One error message has many causes, so tickets bounce between the identity, Immuta and platform teams.
- **Inconsistent.** "Should this person have access?" is answered from memory, and there is pressure to over-grant to close the ticket.
- **Invisible.** Row-level and masking outcomes produce no error at all, so consumers assume the data is wrong.

We do not yet have measured volumes or resolution times for these tickets. Capturing that baseline is part of Phase 0.

## 3. Proposed approach

Three parts, built in this order.

| Part | What it does |
|---|---|
| **1. Read-only tools** | Small functions that each answer one question: which groups a user has, what Immuta holds for them, which Snowflake roles they have, their last failed queries, which accounts their row-level policy allows, which personal-information columns are masked for them. 82 tools are catalogued; 32 form the MVP. |
| **2. Decision engine** | Tested code that compares the access a user *should* have (from policy and entitlements) with the access they *actually* have (from platform grants and query history). The AI model does not make this decision. |
| **3. Chat assistant** | Takes the question in plain language, runs the check, and explains the verdict with the evidence and the next step. |

Every question ends in one of four verdicts, each with a clear owner:

| Should have access | Has access | Meaning | Who acts |
|---|---|---|---|
| Yes | Yes | The session is set up wrongly, or the fault is elsewhere | The user, with the exact fix |
| Yes | No | Platform or sync fault | Platform team, with the evidence attached |
| No | No | Working as designed | The user, told exactly what to request |
| No | Yes | Excess access | Governance, flagged automatically |

The same tools also run on a schedule to detect sync faults and drift between Immuta and the platforms before users report them (Phase 2). Later, they support a guided onboarding journey for new consumers: prerequisites, access requests and sample code (Phase 4).

Architecture in one line: web chat or Teams/Slack, to an AI agent on Amazon Bedrock AgentCore, to a tool gateway (MCP and REST), to tools on AWS Lambda, to the systems of record with read-only access. The full diagram is in [`../diagrams/architecture.png`](../diagrams/architecture.png) and the detail in [`../docs/02-architecture.md`](../docs/02-architecture.md).

## 4. Safeguards

| Safeguard | What it means |
|---|---|
| **Read-only** | The assistant cannot grant or change access, policy, groups or attributes. Its only actions are raising a ticket or escalation, after the user confirms. |
| **No business data** | Tools read metadata, policies and query history. They never read rows from data products. |
| **Identity enforced outside the AI** | Who is asking is taken from single sign-on and checked at the gateway and again in each tool. A user sees only their own access unless their role allows more. |
| **Evidence on every answer** | Each finding cites its source and how fresh the data is. When something could not be checked, the assistant says so. |
| **Reusable** | Tools are exposed as MCP and REST, so another agent, a UI or a script can use them without this assistant. |

Details and the threat model are in [`../docs/07-security-and-governance.md`](../docs/07-security-and-governance.md).

## 5. Benefits

| For | Benefit |
|---|---|
| **Consumers** | Answers in minutes, without raising a ticket |
| **Platform teams** | Fewer tickets that need a specialist; escalations arrive with evidence |
| **Governance** | Consistent, policy-based answers; excess access is surfaced instead of kept |
| **The wider platform** | Reusable tools, and the base for guided consumer onboarding |

Targets we propose to measure after the MVP. These are targets, not measured results; baselines are captured in Phase 0.

| Measure | Target |
|---|---|
| Access tickets resolved without a platform engineer | 60% or more |
| Median time to a diagnosis in chat | Under 2 minutes |
| Correct root cause on the test scenario set | 95% or more |
| Sync faults found before the first user report | 70% or more |
| Mis-routed access tickets | Halved against baseline |

## 6. Scope and roadmap

| Phase | Delivers |
|---|---|
| **0 Foundations** | Open questions answered, read-only access in place, integration facts verified, hosting approved |
| **1 MVP** | Snowflake, Immuta and Entra ID tools; the decision engine; the chat assistant |
| 2 Depth | Scheduled monitoring, ticket and escalation creation, Teams/Slack and web chat |
| 3 Platforms | Databricks and Starburst |
| 4 Onboarding | Guided consumer onboarding |

**This request covers Phases 0 and 1 only.** Later phases are planned after the MVP.

Out of scope: granting or revoking access, reading business data, replacing Immuta or the ticketing and identity tools, and automated remediation.

## 7. What we need

1. **Approval** to proceed with Phase 0 and the MVP.
2. **A delivery team** and a named product owner.
3. **Read-only service identities** in Snowflake, Immuta and Entra ID, granted by each platform owner.
4. **Hosting sign-off** from architecture and security for Amazon Bedrock AgentCore in an approved Region.

Effort and cost have not been estimated yet. The main cost drivers are team time, AI model usage, and a small dedicated Snowflake warehouse for metadata queries. Phase 0 verifies the integration facts and gathers the ticket volumes and user numbers needed for an estimate.

## 8. Risks

| Risk | Response |
|---|---|
| Immuta policies are too varied to evaluate reliably | Cover the most common policies first; return "unknown" for the rest, never a guess |
| Platform metadata lags, so a fresh failure is not yet visible | Every answer states how old its data is; live checks are added selectively |
| Platform owners decline the read permissions | Engage in Phase 0 with a least-privilege list and monitoring of the service identities |
| A wrong "you should have access" answer | Verdicts come only from tested code; automated tests must show zero such errors before release |
| Entitlement information shown to the wrong person | Identity checks at three points outside the AI model; security testing before go-live |
| The agent platform is not approved or not available | Tools are independent of the agent host; a self-hosted fallback is documented |

The full register is in [`../docs/12-assumptions-and-open-questions.md`](../docs/12-assumptions-and-open-questions.md).

## 9. What exists today

- A complete design pack in this repository: solution and architecture documents, a catalog of 82 tools, the decision-engine specification, a security model, 7 architecture decision records, an epic and 73 user stories.
- **No code has been written**, and the design has not yet been verified against our own Immuta, Snowflake and identity tenants. That verification is the first task in Phase 0.

## 10. Next steps if approved

1. Answer the blocking questions on identity set-up, Immuta configuration, row-level and masking implementation, and the telemetry and catalog sources.
2. Request the read-only service identities from each platform owner.
3. Verify every upstream call and query against non-production systems.
4. Create test users that cover each diagnosis outcome.
5. Reach the first milestone: the decision engine giving correct verdicts for every test user from a command line, before any chat agent exists.
