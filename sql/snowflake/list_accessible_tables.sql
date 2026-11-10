-- SF-04 snowflake_list_accessible_tables
-- Binds: :user_name, :limit; :db optional (NULL = all in-scope databases)
-- {scope_databases} is rendered from config/data-mesh-scope.yaml as a quoted IN-list
-- by the handler (allow-listed identifiers only, never user input).
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
    SELECT DISTINCT role_name FROM role_tree UNION SELECT 'PUBLIC'
)
SELECT
    g.table_catalog  AS database_name,
    g.table_schema   AS schema_name,
    g.name           AS table_name,
    g.granted_on     AS object_type,
    ARRAY_AGG(DISTINCT g.grantee_name) WITHIN GROUP (ORDER BY g.grantee_name) AS via_roles
FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES g
JOIN effective_roles r ON r.role_name = g.grantee_name
WHERE g.deleted_on IS NULL
  AND g.granted_to = 'ROLE'
  AND g.privilege IN ('SELECT', 'OWNERSHIP')
  AND g.table_schema IS NOT NULL
  AND g.table_catalog IN ({scope_databases})
  AND (:db IS NULL OR g.table_catalog = :db)
GROUP BY 1, 2, 3, 4
ORDER BY 1, 2, 3
LIMIT :limit;
-- Handler notes: SELECT without USAGE on the parent database/schema is not usable.
-- Mark such rows usable=false using the same chain logic as SF-03 (done in code).
