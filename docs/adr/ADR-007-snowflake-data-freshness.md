# ADR-007: Snowflake data freshness

**Status:** Proposed &nbsp;|&nbsp; **Date:** 2026-11-10

## Context

Snowflake `ACCOUNT_USAGE` views are the simplest, least-privileged way to read users,
grants, query history and policy references for any user. They are not real time: the
documented latency is up to about 45 minutes for `QUERY_HISTORY` and up to 2 to 3 hours
for several others. A user who says "it failed a minute ago" or "I was just added to the
group" may be ahead of the data.

Live alternatives (`SHOW GRANTS`, `INFORMATION_SCHEMA` table functions, `SYSTEM$`
functions) generally need broader privileges on the objects or users concerned.

## Decision

1. **Default to `ACCOUNT_USAGE`** with the minimal `SNOWFLAKE` database roles.
2. **Always return `data_as_of`** and have the agent state the lag when the user's
   timeline falls inside it.
3. **Apply the lag rule** in the engine: a change inside the lag window yields `unknown`
   or `propagation in progress`, not a definite failure.
4. **Ask the user for the query id** when a just-failed query is not yet visible.
5. **Add live paths selectively**, each as its own decision after spike CAA-003 shows the
   privilege needed:
   - grants for one user and one table (candidate: `SHOW GRANTS TO USER` / `TO ROLE`);
   - recent query history for one user (candidate: `INFORMATION_SCHEMA.QUERY_HISTORY_BY_USER`);
   - Iceberg refresh and external volume status (`SYSTEM$` functions).
   A live path is adopted only if it works with a narrowly scoped privilege that the
   Snowflake platform owner accepts.
6. For monitoring (MC-02), use the lagged views and tolerate the lag in thresholds.

## Consequences

- MVP ships with least privilege and honest freshness.
- Some answers will be "not visible yet"; the agent says so and offers a re-check time.
- Live paths can be added per tool without changing contracts (`freshness.mode` changes
  from `lagged` to `live`).

## Alternatives

| Option | Why not chosen |
|---|---|
| Grant the service role broad live privileges (for example MANAGE GRANTS, MONITOR on all users) | Over-privileged for a read-only assistant |
| Mirror metadata into our own store by event | Complex; still lagged; revisit only if lag proves to be the main complaint |
| The on-behalf-of probe as the main check | See ADR-005 |
