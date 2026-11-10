# ADR-005: Service identity, metadata only

**Status:** Proposed &nbsp;|&nbsp; **Date:** 2026-11-10

## Context

To diagnose access the assistant must read identity, entitlement, policy, grant and query
history metadata for any user. It could do so as itself (service identity) or as the user
(on-behalf-of). Running as the user gives ground truth ("can this session read the
table") but a user who lacks access also lacks the rights to see why.

## Decision

1. Tools read **metadata** with dedicated, read-only **service identities** in each
   source system, with least privilege (see the security document).
2. Tools **never read business data**. Row-level and masking answers come from policy
   and entitlements (Immuta's per-user policy information), not from sampling rows.
3. What a requester may see is controlled by the assistant's own scope model (ADR-006),
   since the service identity can see more than the requester.
4. An **optional on-behalf-of probe** (`snowflake_probe_as_user`) may run a
   `SELECT COUNT(*)` with the user's own OAuth token to confirm effective access. It is
   off by default, limited to `self`, returns a count only, and needs a separate security
   approval (story CAA-308).

## Consequences

- Works for users who have no access at all, which is the main use case.
- The service identities are high-value credentials: read-only privileges, key-pair or
  short-lived tokens, network restriction, rotation, and monitoring of their activity.
- The assistant's scope enforcement becomes the control that prevents disclosure; it is
  tested as a security control.
- Without the probe, "actual access" is inferred from grants and may lag; ADR-007 covers
  freshness.

## Note: Immuta Agentic Access API

Immuta has published an Agentic Access API (public preview at the time of writing) that
issues short-lived roles so an agent can query data on behalf of a user within that
user's entitlements. It is not needed for metadata-only diagnosis. It is a candidate for
the optional probe and for any future feature where the assistant runs queries for a
consumer. Evaluate it when it is generally available.

## Alternatives

| Option | Why not chosen |
|---|---|
| Everything on behalf of the user | Users without access cannot see the evidence; needs OAuth to every system |
| Broad admin roles (for example Snowflake ACCOUNTADMIN, Immuta admin) | Violates least privilege; unnecessary for read-only diagnosis |
