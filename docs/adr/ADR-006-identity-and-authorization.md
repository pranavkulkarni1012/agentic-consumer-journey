# ADR-006: Identity and authorisation outside the model

**Status:** Proposed &nbsp;|&nbsp; **Date:** 2026-11-10

## Context

The assistant can read any user's entitlements (ADR-005). A language model can be
persuaded by text. Therefore the model must not be the component that decides who is
asking or what they may see.

## Decision

1. **Identity** is established by SSO at the edge and carried as a validated JWT. Tools
   do not accept the requester as a parameter.
2. **Scopes** (`self`, `support`, `steward`, `platform`) come from identity provider
   group claims, mapped in `config/scopes.yaml`.
3. **Enforcement** at three points, all outside the model:
   - API Gateway JWT authorizer (authentication);
   - Policy in AgentCore (Cedar) on the Gateway: per tool call, may this requester use
     this tool for this subject; write tools need a confirmation token;
   - `caa_core.authz.check()` in every handler, after identity resolution, plus
     field-level filtering by scope.
4. **Write actions** need a confirmation token bound to conversation, requester and
   payload hash, issued only after a dry run is shown to the user.
5. Sign-in: Amazon Cognito federated to Entra ID by default. If the organisation prefers
   fewer components, use Entra ID directly as the OIDC issuer for API Gateway and the
   Gateway's inbound authorizer.

## Consequences

- A prompt injection can at worst make the agent *attempt* a call that is then refused.
- Three checks to keep consistent: generate the Cedar policy and the handler rules from
  the same `scope` field in `specs/tool-catalog.yaml`.
- Machine clients (other agents) must pass the human's token to act for a human.

## Alternatives

| Option | Why not chosen |
|---|---|
| Instruct the model to enforce scope | Not a security control |
| Handler check only | Works, but a central policy point gives uniform audit and defence in depth |
