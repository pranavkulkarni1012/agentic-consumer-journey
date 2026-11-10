# Architecture Decision Records

Status of all records: **Proposed** (2026-11-10). They become Accepted when the architecture
review signs off, or are superseded by a new record. Format: context, decision, consequences,
alternatives.

| ADR | Decision |
|---|---|
| [001](ADR-001-agent-platform.md) | Host the agent on Amazon Bedrock AgentCore Runtime with the Strands Agents SDK |
| [002](ADR-002-tools-as-mcp-and-rest.md) | Implement tools once as Lambda handlers; expose as MCP (AgentCore Gateway) and REST (API Gateway) |
| [003](ADR-003-deterministic-diagnosis-engine.md) | Compute access verdicts in a deterministic engine, not in the model |
| [004](ADR-004-agent-topology.md) | Single orchestrator for MVP; platform specialists from Phase 3 |
| [005](ADR-005-service-identity-metadata-only.md) | Read metadata with service identities; no business data; optional on-behalf-of probe |
| [006](ADR-006-identity-and-authorization.md) | Enforce requester identity and scope outside the model at three points |
| [007](ADR-007-snowflake-data-freshness.md) | Use `ACCOUNT_USAGE` first and state the lag; add live paths selectively |
