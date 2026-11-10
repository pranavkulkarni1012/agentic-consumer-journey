# CLAUDE.md

Guidance for Claude Code (and any coding assistant) working in this repository.

## What this project is

The Consumer Access Assistant (CAA): read-only diagnostic tools, a deterministic diagnosis engine, and a chat agent that explain why a data consumer can or cannot reach a data product on the data mesh (Snowflake first, then Databricks and Starburst; access governed by Immuta using AD groups and user attributes).

**Current state: design only.** The repository holds documentation, specifications, SQL templates and examples. No application code exists yet. Build it story by story from `STORIES.md`.

## Read before you build

| When you are working on | Read |
|---|---|
| Anything | `docs/01-solution-overview.md`, then the story in `STORIES.md` |
| A tool | Its entry in `specs/tool-catalog.yaml` and its section in `docs/04-tool-specifications.md` |
| The diagnosis engine | `docs/06-diagnostic-model.md` (this is the specification) |
| The agent | `docs/05-agent-design.md`, `prompts/system-prompt.md` |
| Auth, data handling | `docs/07-security-and-governance.md` |
| Tests, evals | `docs/09-testing-and-evaluation.md`, `evals/scenarios.yaml` |
| Repo layout, patterns, build order | `docs/10-implementation-guide.md` |
| Something that looks undecided | `docs/12-assumptions-and-open-questions.md` and `docs/adr/` |

## Rules that are not negotiable

1. **Read-only.** Tools never change a source system. Connectors expose read methods only. The only writes are the ticket, escalation and request tools, and they require a confirmation token.
2. **No business data.** Never write code that selects rows from data product tables. Row-level and masking answers come from policy and entitlement metadata.
3. **Verdicts live in the engine.** Any logic that decides whether someone should or does have access belongs in `caa_core/diagnosis` or `caa_core/policy_eval`, with tests. Not in a tool wrapper, not in the agent, not in a prompt.
4. **The requester is never a parameter.** Identity and scopes come from `ToolContext` (populated from the validated token). Call `ctx.resolve_subject()` before any source call.
5. **SQL uses bind variables.** No f-strings, `.format()` or concatenation into SQL. Identifiers go through `caa_core.identifiers.parse_table()`.
6. **Redact before returning.** Query text passes through `redact_sql()`. Sensitive attribute values are not logged.
7. **Evidence for every claim.** A tool result without evidence records fails its contract test. Lagged sources set `data_as_of`.
8. **Unknown beats wrong.** When a policy shape is not understood or a source is down, return `unknown` / `partial` and say what was not checked. Never default to "yes".
9. **Do not invent upstream fields or endpoints.** Use the recorded fixtures in `tests/fixtures/`. If a fixture does not show a field, ask or check current vendor documentation. Items marked VERIFY in the docs have not been confirmed against the real tenants.
10. **Agent platform SDKs change quickly.** For Amazon Bedrock AgentCore, Strands Agents and MCP code, read current official documentation before writing integration code.

## How to work on a story

1. Read the story, its tool entries and the linked doc sections.
2. Propose models (Pydantic input and data) and a test list. Wait for review on anything touching `caa_core`, `config/`, `prompts/` or `infra/`.
3. Write tests first: unit, contract, then connector tests against fixtures.
4. Implement using the `@tool` pattern in `docs/10-implementation-guide.md` section 4.1. Copy the closest existing tool.
5. Run the checks below. Fix what fails.
6. Update `specs/tool-catalog.yaml` if the contract changed, regenerate schemas, and run `python scripts/render_tool_catalog.py`.
7. If you made a design decision the docs did not cover, add or update an ADR.

## Commands

These are the intended commands; create them in story CAA-001 and keep this section current.

```bash
uv sync                                   # install
ruff check . && ruff format --check .     # lint
mypy src                                  # types (strict on caa_core)
pytest tests/unit tests/contract tests/connector   # fast tests
pytest tests/scenarios                    # engine scenarios (no model)
pytest -m integration                     # needs dev credentials
python scripts/render_tool_catalog.py     # regenerate docs/03-tool-catalog.md
python diagrams/architecture.py           # regenerate the architecture diagram
python -m caa_tools.cli <tool> --user <u> [--table <t>]   # call a tool locally
python -m evals.run --set golden          # agent evals
```

## Conventions

- Python 3.12+, type hints everywhere, Pydantic v2 models for all tool inputs and outputs.
- Tool names: `<domain>_<verb>_<noun>`. Tool ids (`SF-05`) and root cause codes (`DIR-001`) are stable; do not renumber.
- One module per tool under `src/caa_tools/<domain>/`. Shared logic goes in `caa_core`.
- Structured logging through `ctx.log` only. No `print`, no raw payloads in logs.
- Time is UTC, ISO 8601. Durations in config carry their unit in the key name.
- Errors map to the codes in `docs/04` section 2. Do not return raw upstream error text.
- Tests: name the persona or fixture in the test id. Add negative cases (not found, denied, partial, upstream error).
- Commits: reference the story id (`CAA-121: privilege chain tool`).

## Things that look tempting and are wrong

| Temptation | Why not |
|---|---|
| Let the model compare grants and policies | Non-deterministic on the one thing that must be right (ADR-003) |
| Give the service role broader privileges "to make it work" | Least privilege is a design constraint (ADR-005, ADR-007) |
| Run `SELECT COUNT(*)` on the data table to check row visibility | Reads business data; use policy information |
| Add a `requester` or `as_user` parameter for testing | Use the fake `ToolContext` in tests |
| Return the whole upstream payload | 16 KB limit; store in evidence, return a summary |
| Skip the freshness label because data "is probably current" | Lag is the top cause of wrong answers |
| Put organisation-specific names in code | They belong in `config/` |

## Ask before

- Adding a dependency.
- Changing a tool contract, a root cause code, the envelope or the scope model.
- Adding any write path or any new privilege for a service identity.
- Changing `prompts/system-prompt.md` (it triggers the full eval suite).
