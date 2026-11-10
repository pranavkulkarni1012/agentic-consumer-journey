# ADR-003: Deterministic diagnosis engine

**Status:** Proposed &nbsp;|&nbsp; **Date:** 2026-11-10

## Context

The central question, "is this user supposed to have access, and do they", is a set
comparison across several systems. A language model can do it from raw payloads most of
the time, but "most of the time" is not acceptable: a wrong "you should have access"
drives over-granting, and a wrong "you should not" sends users in circles. The result
must also be reproducible for audit and testable without a model.

## Decision

Compute expected access, actual access, verdict, root causes and next actions in code
(`caa_core.diagnosis` and `caa_core.policy_eval`). Expose the result through composite
tools (`diagnose_*`). The model chooses the playbook, gathers missing context from the
user, and explains the engine's structured result. The agent prompt forbids stating an
access verdict that did not come from the engine, and evals enforce it.

When the engine cannot decide (unsupported policy construct, source unavailable), it
returns `unknown` / `inconclusive` and lists what was not checked.

## Consequences

- Verdicts are reproducible, unit-testable and auditable; evals can require zero false
  "expected yes".
- The engine must understand policy shapes. Start with the common ones and return
  `unknown` for the rest; coverage grows with usage data.
- One composite call replaces a dozen model-driven calls: lower latency and token cost.
- Granular tools still exist for follow-up questions and exploration.

## Alternatives

| Option | Why not chosen |
|---|---|
| Model reasons over granular tool outputs | Flexible, but non-deterministic on the one thing that must be right |
| Rules only, no model | Loses natural-language intake, clarification and explanation, which are the user-facing value |
