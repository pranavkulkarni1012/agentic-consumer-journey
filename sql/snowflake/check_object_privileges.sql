-- SF-03 snowflake_check_object_privileges
-- Binds: :user_name, :db, :schema, :table   (upper-case unless the object was created quoted)
-- Returns one row per role that holds any link of the chain.
WITH RECURSIVE role_tree (role_name, depth) AS (
    SELECT role, 0
    FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_USERS
    WHERE grantee_name = :user_name AND deleted_on IS NULL
    UNION ALL
    SELECT g.name, t.depth + 1
    FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES g
    JOIN role_tree t ON g.grantee_name = t.role_name
    WHERE g.granted_on = 'ROLE' AND g.granted_to = 'ROLE' AND g.privilege = 'USAGE'
      AND g.deleted_on IS NULL AND t.depth < 12
),
effective_roles AS (
    SELECT DISTINCT role_name FROM role_tree
    UNION
    SELECT 'PUBLIC'
),
grants AS (
    SELECT g.grantee_name AS role_name, g.privilege, g.granted_on, g.name, g.table_catalog, g.table_schema
    FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES g
    JOIN effective_roles r ON r.role_name = g.grantee_name
    WHERE g.deleted_on IS NULL
      AND g.granted_to = 'ROLE'
      AND g.privilege IN ('USAGE', 'SELECT', 'OWNERSHIP')
)
SELECT role_name, has_database_usage, has_schema_usage, has_table_select
FROM (
    SELECT
        role_name,
        MAX(IFF(granted_on = 'DATABASE' AND name = :db, 1, 0))                             AS has_database_usage,
        MAX(IFF(granted_on = 'SCHEMA' AND name = :schema AND table_catalog = :db, 1, 0))   AS has_schema_usage,
        MAX(IFF(name = :table AND table_schema = :schema AND table_catalog = :db
                AND privilege IN ('SELECT', 'OWNERSHIP'), 1, 0))                           AS has_table_select
    FROM grants
    GROUP BY role_name
)
WHERE has_database_usage + has_schema_usage + has_table_select > 0
ORDER BY role_name;
-- Handler logic (in code, not SQL):
--  * Snowflake evaluates privileges across the primary role (and its hierarchy) plus all
--    active secondary roles. So the chain may be satisfied by a COMBINATION of roles:
--      database_usage = any role has it; schema_usage = any; table_select = any.
--  * roles_with_full_chain   = roles (with their hierarchy) that alone satisfy all three.
--  * requires_secondary_roles = chain is satisfied only by combining roles that are not in
--    one hierarchy, e.g. SELECT comes from the Immuta per-user role while USAGE on the
--    database comes from a functional role. This is the most common "expected yes, actual
--    yes, still failing" cause: the session did not have secondary roles active.
--  * The table-level predicate does not filter on granted_on because the value differs
--    by object type (TABLE, VIEW, ICEBERG TABLE, ...). VERIFY in CAA-003.
--  * Future grants and grants through database roles are not in this view's simple form.
--    If the platform uses database roles for data-mesh tables, extend the CTE (CAA-003).
