# ADR-002: Tools as MCP and REST from one implementation

**Status:** Proposed &nbsp;|&nbsp; **Date:** 2026-11-10

## Context

The same capabilities are needed by this agent, by other agents (an existing SRE agent,
developer assistants in the IDE), by a web UI, by scripts, and by the scheduled monitoring
checks. Building them inside one agent would lock them in.

## Decision

Implement each tool once as a Python function in a per-domain Lambda. Expose it:

1. as an **MCP tool** through AgentCore Gateway (Lambda targets), with semantic tool
   search enabled and Policy (Cedar) enforcing scope per call;
2. as a **REST endpoint** through API Gateway (`/v1/...`), described in `api/openapi.yaml`.

Tool input and output models (Pydantic) are the single source for the MCP tool schema,
JSON Schema files and OpenAPI components. `specs/tool-catalog.yaml` is the registry.

## Consequences

- Any MCP client can use the tools; the REST API serves non-agent clients.
- Two front doors to secure. Both use the same JWT issuer and both end in the same
  handler authorisation check.
- One Lambda per domain keeps credentials and egress scoped per source system.
- Schema generation must be automated or the three descriptions will drift (CI check).

## Alternatives

| Option | Why not chosen |
|---|---|
| In-process tools inside the agent | Fast to start; not reusable; no independent scaling or security boundary |
| REST only, with the Gateway translating OpenAPI to MCP | Workable (Gateway supports OpenAPI targets). Chosen against because Lambda targets avoid an extra network hop and API Gateway limits for the agent path. Revisit if operations prefer one front door |
| A self-hosted MCP server (container) | More to operate; no managed auth or tool search |
