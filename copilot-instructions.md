# GitHub Copilot instructions

This repository is the Consumer Access Assistant (CAA): read-only diagnostic tools, a
deterministic diagnosis engine and a chat agent for data-mesh access issues (Immuta,
Snowflake, Entra ID; later Databricks and Starburst).

The full working agreement is in [`CLAUDE.md`](../CLAUDE.md). It applies to Copilot as
well. The short version:

## Always

- Build from the story in `STORIES.md`, the tool entry in `specs/tool-catalog.yaml` and the
  matching section of `docs/04-tool-specifications.md`.
- Follow the `@tool` pattern in `docs/10-implementation-guide.md` section 4.1; copy the
  nearest existing tool.
- Use Pydantic v2 models for inputs and outputs, type hints everywhere, Python 3.12+.
- Use bind variables for SQL and `caa_core.identifiers.parse_table()` for object names.
- Take the requester from `ToolContext`; call `ctx.resolve_subject()` before any source call.
- Attach evidence to every result and set `data_as_of` for lagged sources.
- Redact query text with `redact_sql()` before returning it.
- Write tests first, including not-found, denied, partial and upstream-error cases, against
  the fixtures in `tests/fixtures/`.

## Never

- Write to a source system, or add a connector method that is not a read (the confirmed
  ticket / escalation / request tools are the only exceptions).
- Select rows from data product tables.
- Put access-decision logic in a tool wrapper, the agent or a prompt. It belongs in
  `caa_core/diagnosis` and `caa_core/policy_eval`.
- Add a `requester` / `as_user` parameter to a tool.
- Build SQL with f-strings, `.format()` or concatenation.
- Invent upstream API fields or endpoints. If a fixture does not show it, do not use it.
- Default to "has access" when something is unknown.
- Log names, attribute values, query literals or raw upstream payloads.

## Where things are

| Path | Content |
|---|---|
| `docs/` | Design documentation (start at `01-solution-overview.md`) |
| `docs/06-diagnostic-model.md` | Engine specification: layers, verdict matrix, root cause codes |
| `specs/tool-catalog.yaml` | Source of truth for tools |
| `api/openapi.yaml` | REST contract |
| `sql/snowflake/` | SQL templates per tool |
| `config/examples/` | Configuration templates |
| `prompts/system-prompt.md` | Agent prompt |
| `evals/scenarios.yaml` | Engine and agent scenarios |

## Checks before proposing a change as done

`ruff check .`, `mypy src`, `pytest tests/unit tests/contract tests/connector tests/scenarios`,
and `python scripts/render_tool_catalog.py` when the catalog changed.
