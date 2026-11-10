#!/usr/bin/env python3
"""Consumer Access Assistant - editable architecture diagram for draw.io / Lucidchart.

Writes diagrams/architecture.drawio with two pages holding the same diagram:

  1. "AWS shapes"  - draw.io's AWS Architecture shape library (mxgraph.aws4.*).
                     External systems are plain labelled boxes.
  2. "Icon images" - every icon is an embedded PNG image. Use this page if the importing
                     tool does not recognise the AWS shape library.

Import into Lucidchart with File > Import (draw.io), or open in draw.io directly.

    pip install diagrams pillow
    python diagrams/architecture_drawio.py

Layout coordinates match diagrams/architecture.py (the SVG/PNG version).
"""
import base64
import io
from pathlib import Path
from xml.sax.saxutils import quoteattr

import diagrams
from PIL import Image

HERE = Path(__file__).resolve().parent
RES = Path(diagrams.__file__).resolve().parent.parent / "resources"
ICON = 54
GREY, ORANGE = "#545B64", "#D86613"

# kind -> (draw.io AWS shape, category fill colour, PNG in the icon set)
AWS = {
    "users":       ("users", "#232F3D", "aws/general/users.png"),
    "cloudfront":  ("cloudfront", "#8C4FFF", "aws/network/cloudfront.png"),
    "cognito":     ("cognito", "#DD344C", "aws/security/cognito.png"),
    "apigw":       ("api_gateway", "#E7157B", "aws/network/api-gateway.png"),
    "lambda":      ("lambda", "#ED7100", "aws/compute/lambda.png"),
    "bedrock":     ("bedrock", "#01A88D", "aws/ml/bedrock.png"),
    "agentcore":   ("bedrock_agentcore", "#01A88D", "aws/ml/bedrock.png"),
    "scheduler":   ("eventbridge", "#E7157B", "aws/integration/eventbridge-scheduler.png"),
    "sfn":         ("step_functions", "#E7157B", "aws/integration/step-functions.png"),
    "sns":         ("sns", "#E7157B", "aws/integration/simple-notification-service-sns.png"),
    "s3":          ("s3", "#7AA116", "aws/storage/simple-storage-service-s3.png"),
    "secrets":     ("secrets_manager", "#DD344C", "aws/security/secrets-manager.png"),
    "kms":         ("key_management_service", "#DD344C", "aws/security/key-management-service.png"),
    "cloudwatch":  ("cloudwatch_2", "#E7157B", "aws/management/cloudwatch.png"),
    "cloudtrail":  ("cloudtrail", "#E7157B", "aws/management/cloudtrail.png"),
    "dynamodb":    ("dynamodb", "#C925D1", "aws/database/dynamodb.png"),
    "athena":      ("athena", "#8C4FFF", "aws/analytics/athena.png"),
    "privatelink": ("vpc_privatelink", "#8C4FFF", "aws/network/privatelink.png"),
    "glue":        ("glue", "#8C4FFF", "aws/analytics/glue-data-catalog.png"),
}
# kind -> (badge text, badge colour, PNG in the icon set or None)
EXTERNAL = {
    "teams":      ("Teams /<br>Slack", "#4B53BC", "saas/chat/teams.png"),
    "entra":      ("Entra ID", "#0078D4", "azure/identity/active-directory.png"),
    "immuta":     ("Immuta", "#3B4A5A", None),
    "snowflake":  ("Snow-<br>flake", "#29B5E8", "saas/analytics/snowflake.png"),
    "catalog":    ("Mesh<br>catalog", "#5A6B3B", None),
    "itsm":       ("ITSM<br>IGA", "#6B4A3B", None),
    "databricks": ("Data-<br>bricks", "#E8432E", "onprem/analytics/databricks.png"),
    "starburst":  ("Star-<br>burst", "#DD00A1", "onprem/analytics/trino.png"),
}

# (id, x1, y1, x2, y2, title, fill, stroke, stroke width)
BOXES = [
    ("b_users", 30, 70, 225, 520, "Users and channels", "#F7F9FA", "#879196", 1),
    ("b_aws", 250, 70, 1340, 1085, "AWS account - Consumer Access Assistant", "#FFFFFF", "#232F3E", 2),
    ("b_edge", 270, 125, 500, 700, "1  Edge and sign-in", "#F3F0FA", "#879196", 1),
    ("b_agent", 530, 125, 800, 700, "2  Agent plane (AgentCore)", "#E9F7F3", "#879196", 1),
    ("b_tools", 830, 125, 1320, 700, "3  Tool plane (MCP + REST)", "#FEF4E8", "#879196", 1),
    ("b_state", 830, 730, 1320, 1065, "4  State, secrets, observability", "#EEF3FB", "#879196", 1),
    ("b_monitor", 270, 730, 500, 1065, "5  Proactive monitoring", "#FBEFF3", "#879196", 1),
    ("b_know", 530, 730, 800, 1065, "6  Knowledge", "#F4F8E9", "#879196", 1),
    ("b_sys", 1400, 70, 1870, 1085, "Systems of record (read-only access)", "#F7F9FA", "#879196", 1),
    ("b_prod", 1420, 760, 1850, 1010, "Producer accounts", "#FFFFFF", "#879196", 1),
]

TOOL_X, SYS_X = 1215, 1500
# (id, centre x, centre y, kind, label)
NODES = [
    ("users", 128, 180, "users", "Consumers, support,<br>stewards, platform"),
    ("teams", 128, 400, "teams", "Teams / Slack bot"),
    ("cloudfront", 320, 190, "cloudfront", "CloudFront + WAF<br>web chat UI"),
    ("cognito", 445, 190, "cognito", "Cognito<br>(Entra ID SSO)"),
    ("apigw", 382, 350, "apigw", "API Gateway<br>chat + REST API"),
    ("bff", 382, 530, "lambda", "Lambda<br>chat backend (BFF)"),
    ("model", 600, 190, "bedrock", "Bedrock model<br>(Claude)"),
    ("guardrails", 730, 190, "bedrock", "Bedrock<br>Guardrails"),
    ("runtime", 665, 350, "agentcore", "AgentCore Runtime<br>orchestrator agent"),
    ("memory", 600, 545, "agentcore", "AgentCore<br>Memory"),
    ("identity", 730, 545, "agentcore", "AgentCore<br>Identity"),
    ("gateway", 905, 350, "agentcore", "AgentCore Gateway<br>MCP endpoint + Policy"),
    ("diag", 905, 545, "lambda", "diagnosis engine<br>+ entitlement tools"),
    ("t_identity", TOOL_X, 165, "lambda", "identity tools"),
    ("t_immuta", TOOL_X, 258, "lambda", "immuta tools"),
    ("t_snowflake", TOOL_X, 351, "lambda", "snowflake tools"),
    ("t_catalog", TOOL_X, 444, "lambda", "catalog + telemetry tools"),
    ("t_workflow", TOOL_X, 537, "lambda", "workflow + knowledge tools"),
    ("t_platform", TOOL_X, 630, "lambda", "databricks, starburst,<br>storage tools (phase 3)"),
    ("scheduler", 330, 815, "scheduler", "EventBridge<br>Scheduler"),
    ("sfn", 440, 815, "sfn", "Step Functions<br>check runs"),
    ("checks", 440, 950, "lambda", "drift, sync-lag,<br>health checks"),
    ("sns", 330, 950, "sns", "SNS alerts"),
    ("kb_s3", 600, 850, "s3", "S3 runbooks,<br>guides, code<br>templates"),
    ("kb", 730, 850, "bedrock", "Bedrock<br>Knowledge Base"),
    ("secrets", 900, 815, "secrets", "Secrets<br>Manager"),
    ("kms", 1020, 815, "kms", "KMS"),
    ("cloudwatch", 1140, 815, "cloudwatch", "CloudWatch +<br>AgentCore<br>Observability"),
    ("cloudtrail", 1260, 815, "cloudtrail", "CloudTrail"),
    ("dynamodb", 900, 950, "dynamodb", "DynamoDB<br>cache, findings"),
    ("evidence", 1020, 950, "s3", "S3 evidence,<br>snapshots"),
    ("athena", 1140, 950, "athena", "Athena<br>Immuta audit"),
    ("privatelink", 1260, 950, "privatelink", "PrivateLink /<br>VPC endpoints"),
    ("entra", SYS_X, 165, "entra", "Entra ID / AD<br>groups, attributes"),
    ("immuta", SYS_X, 258, "immuta", "Immuta<br>policies, subscriptions"),
    ("snowflake", SYS_X, 351, "snowflake", "Snowflake<br>grants, query history"),
    ("catalog", SYS_X, 444, "catalog", "Data product catalog<br>+ telemetry"),
    ("itsm", SYS_X, 537, "itsm", "ITSM + identity<br>governance"),
    ("databricks", SYS_X, 630, "databricks", "Databricks<br>Unity Catalog"),
    ("starburst", 1700, 630, "starburst", "Starburst"),
    ("glue", SYS_X, 850, "glue", "Glue Data Catalog"),
    ("lake", 1700, 850, "s3", "S3 Parquet / Iceberg<br>(producer buckets)"),
]

# (x, y, width, text, font size, colour)
NOTES = [
    (430, 22, 1040, "<b>Consumer Access Assistant - Solution Architecture</b>", 22, "#16191F"),
    (830, 612, 150, "deterministic; calls the<br>tool handlers in parallel", 10, "#687078"),
    (1430, 955, 410, "Snowflake, Databricks and Starburst read the registered tables.<br>"
                     "Immuta applies subscription, row and masking policies on each platform.", 10, "#687078"),
    (1415, 1022, 440, "<b>Legend</b>&nbsp; orange = agent tool call (MCP) &nbsp;|&nbsp; solid = request / read<br>"
                      "dashed = later phase, async or alternate path", 10, "#414750"),
]

# (source, target, waypoints, label, dashed, extra style)
BUS = 1000
EDGES = [
    ("users", "cloudfront", [], "chat", False, ""),
    ("users", "teams", [], "", False, ""),
    ("teams", "apigw", [(240, 400), (240, 358)], "bot messages", False, ""),
    ("cloudfront", "apigw", [(320, 342)], "", False, ""),
    ("apigw", "cognito", [], "JWT check", True, ""),
    ("apigw", "bff", [], "", False, ""),
    ("bff", "runtime", [(515, 530), (515, 350)], "InvokeAgentRuntime<br>+ user identity", False, ""),
    ("runtime", "model", [], "reason", False, ""),
    ("runtime", "guardrails", [], "screen", False, ""),
    ("runtime", "memory", [], "", False, ""),
    ("runtime", "identity", [], "", False, ""),
    ("runtime", "b_know", [], "retrieve", False, "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
    ("runtime", "gateway", [], "MCP tools/list,<br>tools/call", False, f"strokeColor={ORANGE};strokeWidth=3;"),
    ("gateway", "diag", [], "", False, ""),
    ("gateway", "t_identity", [(BUS, 350), (BUS, 165)], "", False, ""),
    ("gateway", "t_immuta", [(BUS, 350), (BUS, 258)], "", False, ""),
    ("gateway", "t_snowflake", [], "", False, ""),
    ("gateway", "t_catalog", [(BUS, 350), (BUS, 444)], "", False, ""),
    ("gateway", "t_workflow", [(BUS, 350), (BUS, 537)], "", False, ""),
    ("gateway", "t_platform", [(BUS, 350), (BUS, 630)], "", True, ""),
    ("apigw", "b_tools", [(382, 108), (1215, 108)],
     "REST: Access Diagnostics API - same handlers (web UI, scripts, monitoring)", True,
     "exitX=0.5;exitY=0;entryX=0.786;entryY=0;"),
    ("t_identity", "entra", [], "Microsoft Graph", False, ""),
    ("t_immuta", "immuta", [], "Immuta REST API", False, ""),
    ("t_snowflake", "snowflake", [], "SQL, key-pair,<br>PrivateLink", False, ""),
    ("t_catalog", "catalog", [], "catalog API", False, ""),
    ("t_workflow", "itsm", [], "tickets, requests", False, ""),
    ("t_platform", "databricks", [], "REST + SQL", True, ""),
    ("databricks", "starburst", [], "", True, ""),
    ("t_platform", "glue", [(1371, 646), (1371, 850)], "Glue + S3<br>(phase 3)", True, ""),
    ("glue", "lake", [], "", True, ""),
    ("starburst", "lake", [], "query", True, "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
    ("b_tools", "b_state", [], "secrets, cache, evidence, traces", False, "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
    ("scheduler", "sfn", [], "", False, ""),
    ("sfn", "checks", [], "", False, ""),
    ("checks", "sns", [], "", False, ""),
    ("sns", "teams", [(128, 950)], "alerts", True, ""),
    ("checks", "dynamodb", [(440, 1052), (900, 1052)], "findings (checks call the same tool handlers)", True,
     "exitX=0.5;exitY=1;entryX=0.5;entryY=1;"),
]

LABEL = "verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontColor=#16191F;"
_png_cache: dict[str, str] = {}


def png_uri(rel: str) -> str:
    """Small embedded PNG. draw.io style strings use 'data:image/png,<base64>' (no ';base64')."""
    if rel not in _png_cache:
        img = Image.open(RES / rel).convert("RGBA")
        img.thumbnail((108, 108))
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        _png_cache[rel] = "data:image/png," + base64.b64encode(buf.getvalue()).decode()
    return _png_cache[rel]


def cell(cid, value, style, x, y, w, h):
    return (f'<mxCell id={quoteattr(cid)} value={quoteattr(value)} style={quoteattr(style)} vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')


def node_cells(prefix, nid, cx, cy, kind, label, use_images):
    x, y = cx - ICON / 2, cy - ICON / 2
    cid = f"{prefix}{nid}"
    if kind in AWS:
        shape, fill, png = AWS[kind]
        if use_images:
            style = f"shape=image;imageAspect=0;aspect=fixed;image={png_uri(png)};{LABEL}"
        elif kind == "users":
            style = (f"sketch=0;outlineConnect=0;fillColor={fill};strokeColor=none;dashed=0;aspect=fixed;"
                     f"shape=mxgraph.aws4.users;{LABEL}")
        else:
            style = (f"sketch=0;outlineConnect=0;fillColor={fill};strokeColor=#ffffff;dashed=0;aspect=fixed;"
                     f"shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.{shape};{LABEL}")
        return [cell(cid, label, style, x, y, ICON, ICON)]
    text, colour, png = EXTERNAL[kind]
    if use_images and png:
        style = f"shape=image;imageAspect=0;aspect=fixed;image={png_uri(png)};{LABEL}"
        return [cell(cid, label, style, x, y, ICON, ICON)]
    # labelled badge: the box carries the short name, a text cell below carries the caption
    badge = f"rounded=1;arcSize=14;html=1;fillColor={colour};strokeColor=none;fontColor=#FFFFFF;fontSize=10;fontStyle=1;"
    caption = "text;html=1;align=center;verticalAlign=top;fontSize=11;fontColor=#16191F;strokeColor=none;fillColor=none;"
    return [cell(cid, text, badge, x, y, ICON, ICON),
            cell(f"{cid}_cap", label, caption, cx - 80, cy + ICON / 2 + 2, 160, 34)]


def page(prefix, name, use_images):
    out = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    for bid, x1, y1, x2, y2, title, fill, stroke, sw in BOXES:
        style = (f"rounded=1;arcSize=2;html=1;whiteSpace=wrap;fillColor={fill};strokeColor={stroke};strokeWidth={sw};"
                 "verticalAlign=top;align=left;spacingLeft=10;spacingTop=2;fontStyle=1;fontSize=13;fontColor=#16191F;")
        out.append(cell(f"{prefix}{bid}", title, style, x1, y1, x2 - x1, y2 - y1))
    for nid, cx, cy, kind, label in NODES:
        out.extend(node_cells(prefix, nid, cx, cy, kind, label, use_images))
    for i, (x, y, w, text, size, colour) in enumerate(NOTES):
        style = (f"text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize={size};fontColor={colour};"
                 "strokeColor=none;fillColor=none;")
        out.append(cell(f"{prefix}note{i}", text, style, x, y, w, 30))
    for i, (src, dst, points, label, dashed, extra) in enumerate(EDGES):
        style = (f"endArrow=block;endFill=1;html=1;rounded=0;strokeColor={GREY};strokeWidth=1.5;fontSize=10;"
                 "fontColor=#414750;labelBackgroundColor=#FFFFFF;")
        if dashed:
            style += "dashed=1;dashPattern=6 4;"
        style += extra
        pts = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in points)
        arr = f'<Array as="points">{pts}</Array>' if pts else ""
        out.append(f'<mxCell id="{prefix}e{i}" value={quoteattr(label)} style={quoteattr(style)} edge="1" parent="1" '
                   f'source="{prefix}{src}" target="{prefix}{dst}"><mxGeometry relative="1" as="geometry">{arr}</mxGeometry></mxCell>')
    model = ('<mxGraphModel dx="1600" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
             'fold="1" page="1" pageScale="1" pageWidth="1900" pageHeight="1110" math="0" shadow="0">'
             f'<root>{"".join(out)}</root></mxGraphModel>')
    return f'<diagram id="{prefix}page" name={quoteattr(name)}>{model}</diagram>'


def main():
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<mxfile host="app.diagrams.net" agent="architecture_drawio.py" '
           'version="24.7.17" type="device">'
           + page("a_", "AWS shapes", use_images=False)
           + page("b_", "Icon images", use_images=True)
           + "</mxfile>\n")
    target = HERE / "architecture.drawio"
    target.write_text(xml, encoding="utf-8")
    print(f"wrote {target.name} ({len(xml) // 1024} KB)")


if __name__ == "__main__":
    main()
