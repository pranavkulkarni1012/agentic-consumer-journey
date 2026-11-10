#!/usr/bin/env python3
"""Render docs/03-tool-catalog.md from specs/tool-catalog.yaml.

Usage:  python scripts/render_tool_catalog.py
Requires: pyyaml
"""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "specs" / "tool-catalog.yaml"
OUT = ROOT / "docs" / "03-tool-catalog.md"

DOMAINS = [
    ("identity", "A. Identity and directory (Active Directory / Entra ID)"),
    ("immuta", "B. Immuta"),
    ("snowflake", "C. Snowflake"),
    ("entitlement", "D. Entitlements (derived, cross-system)"),
    ("catalog", "E. Data product catalog"),
    ("telemetry", "E. Telemetry"),
    ("aws", "F. Producer storage (AWS)"),
    ("databricks", "G. Databricks"),
    ("starburst", "H. Starburst"),
    ("diagnosis", "I. Diagnosis (deterministic composites)"),
    ("monitoring", "J. Proactive monitoring"),
    ("workflow", "K. Workflow and knowledge"),
    ("onboarding", "L. Consumer onboarding"),
]

INTRO = """# 03 - Tool Catalog

> **Generated file.** Source of truth: [`specs/tool-catalog.yaml`](../specs/tool-catalog.yaml).
> Edit the YAML and run `python scripts/render_tool_catalog.py`. Detailed contracts for the
> Phase 1 tools are in [04-tool-specifications.md](04-tool-specifications.md).

## How to read this catalog

| Column | Meaning |
|---|---|
| **ID** | Stable id used in stories, tests and traces |
| **Tool** | MCP tool name the agent calls |
| **What it answers** | The question the tool answers, in plain words |
| **How it gets the answer** | Source system and API / SQL |
| **REST endpoint** | Same handler exposed through the Access Diagnostics API |
| **Ph** | Delivery phase: 1 MVP, 2 depth + monitoring, 3 Databricks / Starburst / storage, 4 onboarding |
| **Type** | `read`, `derived` (computed from other tools), `write` (needs confirmation in chat) |
| **Scope** | Minimum requester scope to run the tool for *another* user: `self` < `support` < `steward` < `platform` |
| **Fresh** | `live`, `lagged(max lag)` or `cached(ttl)`. Lagged tools always return `data_as_of`. |

A **(v)** after the tool name means an upstream API or SQL detail must be confirmed against the
deployed product version during spike CAA-003 before the tool is built.

## Your seven starting tools, mapped

| You asked for | Tool(s) |
|---|---|
| 1. User attributes and groups from the Immuta API | `immuta_get_user_entitlements` (IM-02), with `immuta_get_user` (IM-01) |
| 2. Tables / data products the user has access to, from telemetry | `telemetry_get_user_access` (DP-04) |
| 3. Roles the user has on Snowflake | `snowflake_get_user_roles` (SF-02) |
| 4. Tables the user has access to in Snowflake | `snowflake_list_accessible_tables` (SF-04), `snowflake_check_object_privileges` (SF-03) |
| 5. Last 10 failed queries in the last 5 days | `snowflake_get_failed_queries` (SF-05) |
| 6. Row-level security: which accounts the user can see | `entitlement_get_row_visibility` (EN-01), backed by `immuta_get_user_policy_info` (IM-07) |
| 7. What PI access the user has | `entitlement_get_pi_access` (EN-02), backed by IM-07, IM-11 and SF-07 |

## Totals

{totals}

"""


def esc(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def main() -> None:
    spec = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    tools = spec["tools"]
    names = [t["name"] for t in tools]
    ids = [t["id"] for t in tools]
    assert len(names) == len(set(names)), "duplicate tool name"
    assert len(ids) == len(set(ids)), "duplicate tool id"

    by_phase = {}
    for t in tools:
        by_phase[t["phase"]] = by_phase.get(t["phase"], 0) + 1
    totals = "| Phase | Tools |\n|---|---|\n"
    for p in sorted(by_phase):
        totals += f"| {p} | {by_phase[p]} |\n"
    totals += f"| **All** | **{len(tools)}** |"

    out = [INTRO.format(totals=totals)]
    for key, title in DOMAINS:
        rows = [t for t in tools if t["domain"] == key]
        if not rows:
            continue
        out.append(f"## {title}\n")
        out.append("| ID | Tool | What it answers | How it gets the answer | REST endpoint | Ph | Type | Scope | Fresh |")
        out.append("|---|---|---|---|---|---|---|---|---|")
        for t in rows:
            name = f"`{t['name']}`" + (" (v)" if t.get("verify") else "")
            out.append(
                f"| {t['id']} | {name} | {esc(t['summary'])} | {esc(t['how'])} | `{esc(t['rest'])}` "
                f"| {t['phase']} | {t['type']} | {t['scope']} | {esc(t['freshness'])} |"
            )
        out.append("")
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} with {len(tools)} tools")


if __name__ == "__main__":
    main()
