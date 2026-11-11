# 10 - Implementation Guide

For the developer (and their coding assistant) who builds this. Read [`CLAUDE.md`](../CLAUDE.md) first; it is the short version of this guide that the coding assistant loads on every session.

## 1. Before writing code

These unblock everything else. They are stories CAA-001 to CAA-010 in [`STORIES.md`](../STORIES.md).

| # | Do | Why |
|---|---|---|
| 1 | Resolve the open questions marked **blocking** in [12](12-assumptions-and-open-questions.md) | Several design choices depend on them |
| 2 | Run spike CAA-003: call every upstream API and run every SQL template in non-prod; save sanitised responses as fixtures | The documents are verified against vendor docs, not your tenants |
| 3 | Run spike CAA-004: find the catalog and telemetry sources | DP tools are specified as ports until this is known |
| 4 | Get service identities requested (CAA-007) | Lead time, especially where another team runs the platform |
| 5 | Confirm Region, Bedrock model access and AgentCore availability (CAA-002) | Platform decision in ADR-001 depends on it |

## 2. Stack

| Layer | Choice | Notes |
|---|---|---|
| Language | Python 3.12+ | One language for tools, engine, agent, IaC |
| Packaging | `uv` workspace (or Poetry) | `caa_core`, `caa_tools`, `caa_agent`, `infra` |
| Agent framework | Strands Agents SDK | Hosted on AgentCore Runtime with the `bedrock-agentcore` SDK |
| Tool protocol | MCP via AgentCore Gateway (Lambda targets) | Tool schemas generated from `specs/` |
| Validation | Pydantic v2 | Models are the source for JSON Schema and OpenAPI |
| HTTP | `httpx` with retries (`tenacity`) | Immuta, Graph, ITSM |
| Snowflake | `snowflake-connector-python` (key-pair) | Bind variables only |
| SQL parsing | `sqlglot` | Table extraction, literal redaction |
| IaC | AWS CDK (Python). Use Terraform instead if that is the platform standard | Decide in CAA-001 |
| Tests | pytest, Hypothesis, `responses`, moto | |
| Lint / types | ruff, mypy (strict on `caa_core`) | |
| CI | GitHub Actions (or CodePipeline) | |

Check current SDK names and versions at build time; agent platform SDKs change quickly. The coding assistant should read the vendor documentation for AgentCore, Strands and MCP before generating integration code, not rely on memory.

## 3. Repository layout

```
.
├── CLAUDE.md                      # instructions for Claude Code
├── .github/copilot-instructions.md
├── README.md
├── EPIC.md  STORIES.md
├── docs/                          # this documentation
├── specs/
│   ├── tool-catalog.yaml          # source of truth for tools
│   └── schemas/                   # JSON Schema per tool (generated from Pydantic)
├── api/openapi.yaml               # Access Diagnostics REST API
├── config/                        # scopes, group prefixes, attribute map, RLS models,
│   │                              # PI classification, error + root cause catalogs, sync windows
│   └── examples/
├── prompts/system-prompt.md
├── sql/snowflake/                 # SQL templates per tool
├── evals/scenarios.yaml           # agent + engine scenarios
├── diagrams/
├── scripts/
├── src/
│   ├── caa_core/                  # shared library (Lambda layer)
│   │   ├── envelope.py            # ToolResult, Evidence, Freshness
│   │   ├── authz.py               # scope model, check()
│   │   ├── identifiers.py         # parse_table(), normalise names
│   │   ├── redaction.py           # redact_sql(), field filters
│   │   ├── config.py              # typed config loaders
│   │   ├── cache.py               # DynamoDB TTL cache
│   │   ├── evidence.py            # evidence store (S3 + DynamoDB)
│   │   ├── policy_eval.py         # condition tree + evaluator
│   │   ├── errors_catalog.py      # error classification
│   │   ├── diagnosis/             # engine: layers.py, verdict.py, root_causes.py, engine.py
│   │   ├── ports/                 # CatalogPort, TelemetryPort, ItsmPort, IgaPort, PlatformAdapter
│   │   └── connectors/            # graph.py, immuta.py, snowflake.py, ...
│   ├── caa_tools/                 # one package per domain; one module per tool
│   │   ├── identity/  immuta/  snowflake/  entitlement/  catalog/  workflow/
│   │   └── handler.py             # Lambda entry: route by tool name; @tool decorator
│   ├── caa_agent/                 # orchestrator: agent.py, playbooks.py, formatting.py
│   ├── caa_api/                   # BFF + REST routing
│   └── caa_monitor/               # scheduled checks
├── infra/                         # CDK app: network, data, tools, gateway, agent, api, monitor
└── tests/
    ├── unit/  contract/  connector/  integration/  scenarios/
    └── fixtures/                  # sanitised recorded responses, personas
```

## 4. Core patterns

### 4.1 The tool decorator

Every tool is one function. The decorator supplies validation, authorisation, the envelope, timing, audit logging and error mapping, so tool code contains only the logic.

```python
# src/caa_tools/snowflake/get_user_roles.py
from caa_core import tool, ToolContext, Evidence
from caa_core.connectors.snowflake import SnowflakeClient
from .models import GetUserRolesInput, GetUserRolesData

@tool(
    name="snowflake_get_user_roles",
    id="SF-02",
    scope="support",                 # minimum scope to call for another user
    freshness=("lagged", 7200),
    input_model=GetUserRolesInput,
    data_model=GetUserRolesData,
)
def get_user_roles(inp: GetUserRolesInput, ctx: ToolContext) -> GetUserRolesData:
    subject = ctx.resolve_subject(inp.user)          # identity resolution + authz re-check
    if not subject.snowflake.found:
        raise ctx.not_found("No Snowflake user for this person", code="IDN-002")
    rows = ctx.snowflake.query_file(
        "get_user_roles.sql",
        user_name=subject.snowflake.name,
        immuta_role_prefix=ctx.config.immuta.snowflake_role_prefix,
    )
    ctx.add_evidence(Evidence.from_query(
        source="snowflake.account_usage.grants_to_users",
        claim=f"{len(rows)} roles resolved",
        payload=rows,
    ))
    return GetUserRolesData.from_rows(rows)
```

Rules the decorator enforces: input is a Pydantic model (no free-form dicts); the function cannot return without at least one evidence record; exceptions are mapped to the error codes in [04 section 2](04-tool-specifications.md); nothing is logged except through `ctx.log`.

### 4.2 Connectors

- One client per source, created once per container, with timeouts (connect 3 s, read 8 s), retries with jitter on 429/5xx (max 2), and a circuit breaker.
- Connectors expose **read methods only**. The Immuta connector has no generic `request()`; the only non-GET method is the Phase 4 subscribe call, in a separate class.
- Every connector method has a recorded fixture and a contract test.

### 4.3 The engine

`caa_core.diagnosis.engine.diagnose_table_access()` takes a `PlatformAdapter` and the ports, runs the fan-out with `asyncio.gather` and per-source budgets, and returns a `Diagnosis` model. It imports nothing from the agent or from AWS SDKs, so it runs in unit tests with fakes. All thresholds (propagation windows, lags) come from config.

### 4.4 Config

Typed loaders in `caa_core.config`. Files in `config/` are validated in CI against their schema. Unknown keys fail the build. Examples to fill in are under [`config/examples/`](../config/examples/).

### 4.5 Agent

`caa_agent/agent.py` builds the Strands agent with the system prompt, the MCP client pointing at the Gateway URL, and the model id from config. The agent holds no business logic beyond playbook hints and answer formatting. Keep it that way: if you are tempted to add an `if` about access to the agent, it belongs in the engine.

## 5. Build order

Each step ends with something that runs. Story ids in brackets.

| Step | Build | Proves |
|---|---|---|
| 1 | Repo, CI, `caa_core` foundation: envelope, authz, identifiers, redaction, config (CAA-001, 008, 009) | The contract every tool shares |
| 2 | Baseline infrastructure (CAA-010) and service identities (CAA-007) | Connectivity to each source from a Lambda |
| 3 | Snowflake connector + SF-01, SF-02 (CAA-120) | First tool end to end, locally and in `dev` |
| 4 | Graph and Immuta connectors + ID and IM read tools (CAA-101, 102, 110, 111) | All three systems reachable |
| 5 | Policy normaliser and evaluator (CAA-112, 113) | Expected access, deterministic |
| 6 | Remaining Snowflake tools (CAA-121 to 123) | Actual access |
| 7 | Diagnosis engine + DX-01 (CAA-150, 151), with engine scenario tests | The core value, with no model involved |
| 8 | Gateway registration, Cedar policy, REST projection (CAA-160, 161) | Tools callable over MCP and REST with scopes enforced |
| 9 | Orchestrator agent + chat API (CAA-170, 171, 172) | First conversation |
| 10 | Eval harness and golden set (CAA-180) | Quality gate in CI |
| 11 | EN-01, EN-02, EN-03, DX-02, catalog and telemetry adapters, KB (CAA-130 to 141, 152, 162) | Full MVP scope |
| 12 | Observability, security review, pilot (CAA-181 to 183) | Go-live |

Steps 3 to 7 need no AWS agent services at all. The engine can be demonstrated from a CLI (`python -m caa_tools.cli diagnose-table-access --user … --table …`) before any agent exists. Do that demo; it de-risks the hard part early.

## 6. Working with Claude Code or GitHub Copilot

### 6.1 Set-up

- `CLAUDE.md` at the repo root is loaded automatically by Claude Code. GitHub Copilot reads `.github/copilot-instructions.md`; the file currently sits at the repo root as `copilot-instructions.md` and must be moved into `.github/` to take effect (story CAA-001).
- Keep both short and factual. Detailed context stays in `docs/`; the instruction files point to it.
- Give the assistant the fixture files from CAA-003. Real response shapes prevent invented fields.

### 6.2 A prompt pattern that works per story

```
Implement story CAA-121 from STORIES.md.

Read first:
- docs/04-tool-specifications.md, sections for SF-03 and SF-04
- specs/tool-catalog.yaml entries SF-03, SF-04
- sql/snowflake/check_object_privileges.sql and list_accessible_tables.sql
- src/caa_tools/snowflake/get_user_roles.py as the pattern to follow
- tests/fixtures/snowflake/ for real response shapes

Then:
1. Propose the Pydantic input and data models and the test list. Stop for my review.
2. After I approve, write tests first (unit + contract), then the handlers.
3. Run ruff, mypy and pytest. Fix failures.
4. Update specs/schemas/ and re-render docs/03-tool-catalog.md.

Constraints: follow CLAUDE.md. Bind variables only. No new dependencies without asking.
Do not change caa_core without telling me why.
```

### 6.3 Review checklist for assistant-written code

| Check | Look for |
|---|---|
| Invented API fields | Any field not present in a fixture or vendor doc. Ask for the source. |
| SQL safety | f-strings or `.format()` touching SQL |
| Authz | `ctx.resolve_subject()` called before any source call |
| Evidence | Every claim has an evidence record with `data_as_of` |
| Redaction | Query text passes through `redact_sql` |
| Logic leakage | Access reasoning in the agent or a tool, not in the engine |
| Tests | Negative cases: not found, denied, partial, upstream error |
| Scope creep | New write paths, broader privileges, extra dependencies |

### 6.4 Useful assistant set-up

- A project slash command or skill `new-tool` that scaffolds the catalog entry, models, handler, fixtures and tests from the pattern in section 4.1.
- A sub-agent restricted to read-only tools for "explain this fixture / vendor response".
- A pre-commit hook running ruff, mypy, schema validation of `config/` and `specs/`, and the catalog render check.
- Connect the deployed `dev` Gateway as an MCP server in the IDE so the developer can call real tools while building the next ones.

## 7. Environments and data

| Env | Sources | Model | Purpose |
|---|---|---|---|
| local | Fixtures and fakes | Optional (Bedrock dev account) | Unit, contract, engine scenarios |
| dev | Non-prod Immuta, Snowflake, Entra test tenant; seeded personas | Bedrock | Integration, evals |
| test | Same as dev, production-like config | Bedrock | Release candidate, E2E, load |
| prod | Production metadata, read-only | Bedrock | Live |

Fixtures must be sanitised: replace names, emails, account ids and query literals before committing. A script `scripts/sanitise_fixture.py` does this deterministically (story CAA-003).

## 8. Definition of done (story level)

1. Acceptance criteria in `STORIES.md` met and demonstrated in `dev`.
2. Tests at the levels required by [09](09-testing-and-evaluation.md) pass in CI.
3. Eval suite passes its gates when the change touches prompt, tool descriptions, engine or config.
4. Docs updated: catalog re-rendered, spec section amended, ADR added if a decision changed.
5. No new high or medium findings from static analysis or secret scan.
6. Metrics and audit records visible for the new behaviour.
7. Reviewed by a second engineer; `config/`, `prompts/`, `infra/` changes reviewed by CODEOWNERS.
