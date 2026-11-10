# ADR-001: Agent platform

**Status:** Proposed &nbsp;|&nbsp; **Date:** 2026-11-10

## Context

We need to host a conversational agent that calls 30 to 80 tools, carries the end user's
identity to those tools, keeps session state, and is observable and evaluable. The data
platform runs on AWS. The team already builds agents and MCP servers and wants the tools
to be reusable by other agents.

## Decision

Host the orchestrator on **Amazon Bedrock AgentCore Runtime**, built with the **Strands
Agents SDK**, using Anthropic Claude models on Amazon Bedrock. Use AgentCore Gateway for
tools (ADR-002), AgentCore Identity for inbound and outbound auth, AgentCore Memory for
session and preference memory, AgentCore Observability and Evaluations for traces and
quality.

## Consequences

- Managed session isolation, identity propagation and MCP tooling; less undifferentiated
  infrastructure to build.
- The service is evolving quickly. Pin SDK versions, read current documentation at build
  time, and keep agent code thin so the host can be changed.
- Region and feature availability must be confirmed (CAA-002).
- Because business logic lives in tools and the engine, replacing the agent host affects
  `caa_agent/` only.

## Alternatives

| Option | Why not chosen |
|---|---|
| Amazon Bedrock Agents with action groups | Simpler start, but less control of the loop and MCP reuse; tools would be tied to action-group schemas |
| Self-hosted (LangGraph or Strands on ECS Fargate / Lambda) | Full control; more to build and operate for identity, memory and observability. **This is the fallback** if AgentCore is not approved or not in Region |
| Extend an existing in-house agent | Viable and encouraged: the tools are MCP, so an existing agent can adopt them. Decide after Q16 |

## Fallback trigger

If CAA-002 finds AgentCore unavailable or not approved: run the same Strands agent in a
container on ECS Fargate behind the BFF, host the MCP server as a Lambda-backed HTTP
service behind API Gateway with a JWT authorizer, and implement the scope check in a
Lambda authorizer plus `caa_core.authz`.
