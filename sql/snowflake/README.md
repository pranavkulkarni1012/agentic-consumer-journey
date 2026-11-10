# Snowflake SQL templates

One file per tool. These are **design-time templates**: they have not been run against
your account. Spike CAA-003 executes each one in non-prod and fixes column or value
differences before the handlers are written.

Rules for handlers that use these files:

1. **Bind variables only** (`:name`). Never build SQL by string concatenation from tool
   input. The single exception is `{scope_databases}`, rendered from the allow-list in
   `config/data-mesh-scope.yaml`.
2. Set a query tag on every session:
   `ALTER SESSION SET QUERY_TAG = '{"app":"caa","tool":"<tool>","trace_id":"<id>"}'`.
3. Every query has a time-bounded predicate on a history view. Keep it.
4. Identifiers are matched as stored. Unquoted identifiers are upper-case; normalise in
   `caa_core.identifiers.parse_table()` and keep quoted, case-sensitive names as given.
5. Return `data_as_of` = query time minus the documented lag of the slowest view used.

| File | Tool | Views |
|---|---|---|
| `00_service_role_setup.sql` | - | Service role, warehouse, user |
| `get_user.sql` | SF-01 | `USERS` |
| `get_user_roles.sql` | SF-02 | `GRANTS_TO_USERS`, `GRANTS_TO_ROLES` |
| `check_object_privileges.sql` | SF-03 | `GRANTS_TO_USERS`, `GRANTS_TO_ROLES` |
| `list_accessible_tables.sql` | SF-04 | `GRANTS_TO_USERS`, `GRANTS_TO_ROLES` |
| `get_failed_queries.sql` | SF-05 | `QUERY_HISTORY` |
| `get_query_details.sql` | SF-06 | `QUERY_HISTORY`, `ACCESS_HISTORY` |
| `get_table_policies.sql` | SF-07 | `POLICY_REFERENCES` |
| `get_table_status.sql` | SF-08 | `TABLES` |
| `get_login_history.sql` | SF-09 | `LOGIN_HISTORY` |
| `get_access_history.sql` | SF-10 | `ACCESS_HISTORY`, `QUERY_HISTORY` |
| `get_grant_changes.sql` | SF-13 | `GRANTS_TO_USERS`, `GRANTS_TO_ROLES` |
