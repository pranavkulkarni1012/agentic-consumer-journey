-- SF-13 snowflake_get_grant_changes   (Phase 2)
-- Binds: :user_name, :days; :db/:schema/:table optional
-- Shows role grants to the user and object grants on the table that were created or
-- removed inside the window.
SELECT 'ROLE_TO_USER' AS change_scope,
       IFF(deleted_on IS NOT NULL AND deleted_on >= DATEADD('day', -:days, CURRENT_TIMESTAMP()), 'revoked', 'granted') AS action,
       COALESCE(deleted_on, created_on) AS changed_at,
       role AS role_name, NULL AS privilege, NULL AS object_name, granted_by
FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_USERS
WHERE grantee_name = :user_name
  AND (created_on >= DATEADD('day', -:days, CURRENT_TIMESTAMP())
    OR deleted_on >= DATEADD('day', -:days, CURRENT_TIMESTAMP()))
UNION ALL
SELECT 'OBJECT_TO_ROLE',
       IFF(deleted_on IS NOT NULL AND deleted_on >= DATEADD('day', -:days, CURRENT_TIMESTAMP()), 'revoked', 'granted'),
       COALESCE(deleted_on, created_on),
       grantee_name, privilege, table_catalog || '.' || table_schema || '.' || name, granted_by
FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES
WHERE :table IS NOT NULL
  AND name = :table AND table_schema = :schema AND table_catalog = :db
  AND (created_on >= DATEADD('day', -:days, CURRENT_TIMESTAMP())
    OR deleted_on >= DATEADD('day', -:days, CURRENT_TIMESTAMP()))
ORDER BY changed_at DESC
LIMIT 200;
