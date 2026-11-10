#!/usr/bin/env python3
"""Consumer Access Assistant - solution architecture (diagram as code).

Writes diagrams/architecture.svg and diagrams/architecture.png.

    pip install diagrams cairosvg
    python diagrams/architecture.py

Icons are the AWS architecture icons (and partner icons) bundled with the `diagrams`
package; this script only uses that package as an icon library and does its own layout,
so positions are stable and easy to edit: change a coordinate, re-run.

Amazon Bedrock AgentCore has no dedicated icon in this icon set, so AgentCore Runtime,
Gateway, Identity and Memory use the Amazon Bedrock icon with an explicit label.
Immuta, the mesh catalog, ITSM and identity governance use neutral text badges.
"""
import base64
from pathlib import Path

import diagrams

HERE = Path(__file__).resolve().parent
RES = Path(diagrams.__file__).resolve().parent.parent / "resources"
W, H = 1900, 1110
ICON = 54
FONT = "DejaVu Sans, Helvetica, Arial, sans-serif"
GREY = "#545B64"
ORANGE = "#D86613"

out = []


def icon_data(rel: str) -> str:
    return "data:image/png;base64," + base64.b64encode((RES / rel).read_bytes()).decode()


def box(x1, y1, x2, y2, title, fill, stroke="#879196", bold=True, sw=1.2):
    out.append(f'<rect x="{x1}" y="{y1}" width="{x2 - x1}" height="{y2 - y1}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    weight = "700" if bold else "400"
    out.append(f'<text x="{x1 + 12}" y="{y1 + 21}" font-family="{FONT}" font-size="13.5" font-weight="{weight}" fill="#16191F">{title}</text>')


def label(cx, y, text, size=11.5, fill="#16191F", weight="400", anchor="middle"):
    for i, line in enumerate(text.split("\n")):
        out.append(f'<text x="{cx}" y="{y + i * (size + 2.5)}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}">{line}</text>')


def node(cx, cy, rel, text):
    out.append(f'<image x="{cx - ICON / 2}" y="{cy - ICON / 2}" width="{ICON}" height="{ICON}" href="{icon_data(rel)}"/>')
    label(cx, cy + ICON / 2 + 15, text)


def badge(cx, cy, text, colour, caption):
    out.append(f'<rect x="{cx - ICON / 2}" y="{cy - ICON / 2}" width="{ICON}" height="{ICON}" rx="8" fill="{colour}"/>')
    lines = text.split("\n")
    y0 = cy - (len(lines) - 1) * 6.5 + 4
    for i, line in enumerate(lines):
        out.append(f'<text x="{cx}" y="{y0 + i * 13}" text-anchor="middle" font-family="{FONT}" font-size="10.5" font-weight="700" fill="#FFFFFF">{line}</text>')
    label(cx, cy + ICON / 2 + 15, caption)


def arrow(points, text=None, tpos=None, dashed=False, colour=GREY, width=1.5):
    d = "M " + " L ".join(f"{x},{y}" for x, y in points)
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    marker = "arrow" if colour == GREY else "arrow-o"
    out.append(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}"{dash} marker-end="url(#{marker})" stroke-linejoin="round"/>')
    if text:
        tx, ty = tpos
        lines = text.split("\n")
        wide = max(len(line) for line in lines) * 6.3 + 8
        out.append(f'<rect x="{tx - wide / 2}" y="{ty - 11}" width="{wide}" height="{len(lines) * 13.5 + 3}" fill="#FFFFFF" opacity="0.9" rx="3"/>')
        label(tx, ty, text, size=10.5, fill="#414750")


R = ICON / 2  # half icon
LBL1, LBL2 = 22, 36  # space taken below an icon by a 1-line / 2-line label

# ------------------------------------------------------------------ frame
out.append(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')
label(W / 2, 40, "Consumer Access Assistant - Solution Architecture", size=22, weight="700")

box(30, 70, 225, 520, "Users and channels", "#F7F9FA")
box(250, 70, 1340, 1085, "AWS account - Consumer Access Assistant", "#FFFFFF", stroke="#232F3E", sw=2)
box(270, 125, 500, 700, "1  Edge and sign-in", "#F3F0FA")
box(530, 125, 800, 700, "2  Agent plane (AgentCore)", "#E9F7F3")
box(830, 125, 1320, 700, "3  Tool plane (MCP + REST)", "#FEF4E8")
box(830, 730, 1320, 1065, "4  State, secrets, observability", "#EEF3FB")
box(270, 730, 500, 1065, "5  Proactive monitoring", "#FBEFF3")
box(530, 730, 800, 1065, "6  Knowledge", "#F4F8E9")
box(1400, 70, 1870, 1085, "Systems of record (read-only access)", "#F7F9FA")
box(1420, 760, 1850, 1010, "Producer accounts", "#FFFFFF", bold=False)

# ------------------------------------------------------------------ nodes
node(128, 180, "aws/general/users.png", "Consumers, support,\nstewards, platform")
node(128, 400, "saas/chat/teams.png", "Teams / Slack bot")

node(320, 190, "aws/network/cloudfront.png", "CloudFront + WAF\nweb chat UI")
node(445, 190, "aws/security/cognito.png", "Cognito\n(Entra ID SSO)")
node(382, 350, "aws/network/api-gateway.png", "API Gateway\nchat + REST API")
node(382, 530, "aws/compute/lambda.png", "Lambda\nchat backend (BFF)")

node(600, 190, "aws/ml/bedrock.png", "Bedrock model\n(Claude)")
node(730, 190, "aws/ml/bedrock.png", "Bedrock\nGuardrails")
node(665, 350, "aws/ml/bedrock.png", "AgentCore Runtime\norchestrator agent")
node(600, 545, "aws/ml/bedrock.png", "AgentCore\nMemory")
node(730, 545, "aws/ml/bedrock.png", "AgentCore\nIdentity")

node(905, 350, "aws/ml/bedrock.png", "AgentCore Gateway\nMCP endpoint + Policy")
node(905, 545, "aws/compute/lambda.png", "diagnosis engine\n+ entitlement tools")
label(905, 624, "deterministic; calls the\ntool handlers in parallel", size=10, fill="#687078")
TOOL_X = 1215
tools = [
    (165, "identity tools"),
    (258, "immuta tools"),
    (351, "snowflake tools"),
    (444, "catalog + telemetry\ntools"),
    (537, "workflow + knowledge\ntools"),
    (630, "databricks, starburst,\nstorage tools (phase 3)"),
]
for y, text in tools:
    out.append(f'<image x="{TOOL_X - R}" y="{y - R}" width="{ICON}" height="{ICON}" href="{icon_data("aws/compute/lambda.png")}"/>')
    label(TOOL_X - R - 8, y - 3 if "\n" in text else y + 4, text, anchor="end")

node(330, 815, "aws/integration/eventbridge-scheduler.png", "EventBridge\nScheduler")
node(440, 815, "aws/integration/step-functions.png", "Step Functions\ncheck runs")
node(440, 950, "aws/compute/lambda.png", "drift, sync-lag,\nhealth checks")
node(330, 950, "aws/integration/simple-notification-service-sns.png", "SNS alerts")

node(600, 850, "aws/storage/simple-storage-service-s3.png", "S3 runbooks,\nguides, code\ntemplates")
node(730, 850, "aws/ml/bedrock.png", "Bedrock\nKnowledge Base")

node(900, 815, "aws/security/secrets-manager.png", "Secrets\nManager")
node(1020, 815, "aws/security/key-management-service.png", "KMS")
node(1140, 815, "aws/management/cloudwatch.png", "CloudWatch +\nAgentCore\nObservability")
node(1260, 815, "aws/management/cloudtrail.png", "CloudTrail")
node(900, 950, "aws/database/dynamodb.png", "DynamoDB\ncache, findings")
node(1020, 950, "aws/storage/simple-storage-service-s3.png", "S3 evidence,\nsnapshots")
node(1140, 950, "aws/analytics/athena.png", "Athena\nImmuta audit")
node(1260, 950, "aws/network/privatelink.png", "PrivateLink /\nVPC endpoints")

SYS_X = 1500
node(SYS_X, 165, "azure/identity/active-directory.png", "Entra ID / AD\ngroups, attributes")
badge(SYS_X, 258, "Immuta", "#3B4A5A", "Immuta\npolicies, subscriptions")
node(SYS_X, 351, "saas/analytics/snowflake.png", "Snowflake\ngrants, query history")
badge(SYS_X, 444, "Mesh\ncatalog", "#5A6B3B", "Data product catalog\n+ telemetry")
badge(SYS_X, 537, "ITSM\nIGA", "#6B4A3B", "ITSM + identity\ngovernance")
node(SYS_X, 630, "onprem/analytics/databricks.png", "Databricks\nUnity Catalog")
node(1700, 630, "onprem/analytics/trino.png", "Starburst")
node(SYS_X, 850, "aws/analytics/glue-data-catalog.png", "Glue Data Catalog")
node(1700, 850, "aws/storage/simple-storage-service-s3.png", "S3 Parquet / Iceberg\n(producer buckets)")
label(1635, 965, "Snowflake, Databricks and Starburst read the registered tables.\nImmuta applies subscription, row and masking policies on each platform.", size=10, fill="#687078")

# ------------------------------------------------------------------ flows
# users -> edge
arrow([(128 + R + 4, 180), (320 - R - 4, 188)], "chat", (222, 173))
arrow([(128, 180 + R + LBL2 + 6), (128, 400 - R - 4)])
arrow([(128 + R + 4, 400), (240, 400), (240, 358), (382 - R - 4, 358)], "bot messages", (240, 422))
arrow([(320, 190 + R + LBL2 + 6), (320, 342), (382 - R - 4, 342)])
arrow([(402, 350 - R - 4), (440, 190 + R + LBL2 + 6)], "JWT check", (462, 284), dashed=True)
arrow([(382, 350 + R + LBL2 + 6), (382, 530 - R - 4)])
arrow([(382 + R + 4, 530), (515, 530), (515, 350), (665 - R - 4, 350)], "InvokeAgentRuntime\n+ user identity", (515, 446))

# agent plane
arrow([(652, 350 - R - 4), (608, 190 + R + LBL2 + 6)], "reason", (604, 292))
arrow([(678, 350 - R - 4), (722, 190 + R + LBL2 + 6)], "screen", (730, 292))
arrow([(648, 350 + R + LBL2 + 6), (608, 545 - R - 4)])
arrow([(682, 350 + R + LBL2 + 6), (722, 545 - R - 4)])
arrow([(665, 350 + R + LBL2 + 6), (665, 730)], "retrieve", (665, 662))

# agent -> gateway -> tools
arrow([(665 + R + 4, 350), (905 - R - 4, 350)], "MCP tools/list,\ntools/call", (790, 326), colour=ORANGE, width=2.6)
BUS_X = 1000
out.append(f'<path d="M {905 + R + 4},350 L {BUS_X},350 M {BUS_X},165 L {BUS_X},630" fill="none" stroke="{GREY}" stroke-width="1.5"/>')
for y, _ in tools:
    arrow([(BUS_X, y), (BUS_X + 26, y)], dashed=(y == 630))
arrow([(905, 350 + R + LBL2 + 6), (905, 545 - R - 4)])

# REST path over the top
arrow([(382, 350 - R - 4), (382, 108), (TOOL_X, 108), (TOOL_X, 165 - R - 4)],
      "REST: Access Diagnostics API - same handlers (web UI, scripts, monitoring)", (860, 105), dashed=True)

# tools -> systems of record
arrow([(TOOL_X + R + 4, 165), (SYS_X - R - 4, 165)], "Microsoft Graph", (1366, 157))
arrow([(TOOL_X + R + 4, 258), (SYS_X - R - 4, 258)], "Immuta REST API", (1366, 250))
arrow([(TOOL_X + R + 4, 351), (SYS_X - R - 4, 351)], "SQL, key-pair,\nPrivateLink", (1366, 337))
arrow([(TOOL_X + R + 4, 444), (SYS_X - R - 4, 444)], "catalog API", (1366, 436))
arrow([(TOOL_X + R + 4, 537), (SYS_X - R - 4, 537)], "tickets, requests", (1366, 529))
arrow([(TOOL_X + R + 4, 624), (SYS_X - R - 4, 624)], "REST + SQL", (1366, 616), dashed=True)
arrow([(SYS_X + R + 4, 630), (1700 - R - 4, 630)], dashed=True)
arrow([(TOOL_X + R + 4, 646), (1371, 646), (1371, 850), (SYS_X - R - 4, 850)], "Glue + S3\n(phase 3)", (1371, 730), dashed=True)
arrow([(SYS_X + R + 4, 850), (1700 - R - 4, 850)], dashed=True)
arrow([(1700, 630 + R + LBL1 + 6), (1700, 850 - R - 4)], "query", (1700, 748), dashed=True)

# tool plane -> state
arrow([(1075, 700), (1075, 730)])
label(1090, 719, "secrets, cache, evidence, traces", size=10.5, fill="#414750", anchor="start")

# monitoring
arrow([(330 + R + 4, 815), (440 - R - 4, 815)])
arrow([(440, 815 + R + LBL2 + 6), (440, 950 - R - 4)])
arrow([(440 - R - 4, 950), (330 + R + 4, 950)])
arrow([(330 - R - 4, 950), (128, 950), (128, 400 + R + LBL1 + 8)], "alerts", (190, 942), dashed=True)
arrow([(440, 950 + R + LBL2 + 6), (440, 1052), (900, 1052), (900, 950 + R + LBL2 + 6)],
      "findings (checks call the same tool handlers)", (670, 1048), dashed=True)

# ------------------------------------------------------------------ legend
lx, ly = 1420, 1035
out.append(f'<path d="M {lx},{ly} L {lx + 40},{ly}" stroke="{ORANGE}" stroke-width="2.6" marker-end="url(#arrow-o)"/>')
label(lx + 50, ly + 4, "agent tool call (MCP)", size=10.5, anchor="start")
out.append(f'<path d="M {lx + 200},{ly} L {lx + 240},{ly}" stroke="{GREY}" stroke-width="1.5" marker-end="url(#arrow)"/>')
label(lx + 250, ly + 4, "request / read", size=10.5, anchor="start")
out.append(f'<path d="M {lx},{ly + 24} L {lx + 40},{ly + 24}" stroke="{GREY}" stroke-width="1.5" stroke-dasharray="6 4" marker-end="url(#arrow)"/>')
label(lx + 50, ly + 28, "later phase, async or alternate path", size=10.5, anchor="start")

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{GREY}"/></marker>
<marker id="arrow-o" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{ORANGE}"/></marker>
</defs>
{chr(10).join(out)}
</svg>'''

(HERE / "architecture.svg").write_text(svg, encoding="utf-8")
try:
    import cairosvg

    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(HERE / "architecture.png"), scale=2)
    print("wrote architecture.svg and architecture.png")
except ImportError:
    print("wrote architecture.svg (install cairosvg to also write the PNG)")
