# ADR-004: Agent topology

**Status:** Proposed &nbsp;|&nbsp; **Date:** 2026-11-10

## Context

The catalog reaches about 80 tools across three platforms. Multi-agent designs
(supervisor plus specialists) help with context size and domain focus but add latency,
cost and evaluation complexity.

## Decision

- **Phases 1 and 2:** one orchestrator agent. It sees the composite, entitlement,
  monitoring and knowledge tools directly and finds granular tools through the Gateway's
  semantic tool search.
- **Phase 3 onward:** add platform specialists (Snowflake, Databricks, Starburst) and an
  onboarding guide as agents-as-tools behind the same orchestrator. The diagnosis engine
  stays single and platform-neutral behind a `PlatformAdapter` interface.

## Consequences

- MVP is simple to build, trace and evaluate.
- The move to specialists is additive: prompts and tool subsets per platform, no change
  to the engine or the tool contracts.
- Trigger to split earlier: tool-selection accuracy on the eval set drops below 95%, or
  the orchestrator prompt plus tool definitions exceed the context budget set in config.

## Alternatives

| Option | Why not chosen |
|---|---|
| Multi-agent from day one | Unneeded for one platform; harder to evaluate |
| One agent forever | Tool descriptions for three platforms compete; platform-specific guidance bloats the prompt |
