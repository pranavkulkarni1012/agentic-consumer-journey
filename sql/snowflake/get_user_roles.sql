-- SF-02 snowflake_get_user_roles
-- Binds: :user_name (Snowflake NAME from SF-01), :immuta_role_prefix (e.g. 'IMMUTA_USER_')
-- Source lag: up to ~2 hours (GRANTS_TO_USERS, GRANTS_TO_ROLES)
WITH RECURSIVE role_tree (role_name, root_role, depth, grant_path) AS (
    SELECT role, role, 0, role
    FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_USERS
    WHERE grantee_name = :user_name
      AND deleted_on IS NULL
    UNION ALL
    SELECT g.name, t.root_role, t.depth + 1, t.grant_path || ' > ' || g.name
    FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES g
    JOIN role_tree t
      ON g.grantee_name = t.role_name
    WHERE g.granted_on = 'ROLE'
      AND g.granted_to = 'ROLE'
      AND g.privilege  = 'USAGE'
      AND g.deleted_on IS NULL
      AND t.depth < 12
)
SELECT
    role_name,
    MIN(depth)                                   AS depth,
    MIN_BY(grant_path, depth)                    AS grant_path,
    MIN_BY(root_role, depth)                     AS via_direct_role,
    STARTSWITH(UPPER(role_name), UPPER(:immuta_role_prefix)) AS is_immuta_managed
FROM role_tree
GROUP BY role_name
ORDER BY depth, role_name;
-- Handler notes:
--  * PUBLIC is implicit for every user; append it in code, do not query for it.
--  * immuta_role_present = any row with is_immuta_managed.
--  * The Immuta per-user role is named <PREFIX>_USER_<username>; the prefix is set in
--    Immuta app settings. Read it from config, do not hard-code.
