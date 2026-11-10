-- SF-01 snowflake_get_user
-- Binds: :user  (login name, user name or email; matched case-insensitively)
-- Source lag: up to ~2 hours (ACCOUNT_USAGE.USERS)
SELECT
    name,
    login_name,
    display_name,
    email,
    type,
    disabled,
    snowflake_lock,
    locked_until_time,
    expires_at,
    default_role,
    default_warehouse,
    default_namespace,
    default_secondary_role,
    has_password,
    has_rsa_public_key,
    ext_authn_uid,
    last_success_login,
    password_last_set_time,
    created_on,
    deleted_on
FROM SNOWFLAKE.ACCOUNT_USAGE.USERS
WHERE (UPPER(name) = UPPER(:user)
    OR UPPER(login_name) = UPPER(:user)
    OR UPPER(email) = UPPER(:user))
ORDER BY (deleted_on IS NULL) DESC, created_on DESC
LIMIT 5;
-- Handler notes:
--  * more than one live row = ambiguous identity -> status "partial", warning IDN-004
--  * only deleted rows = user was dropped -> found=false, include deleted_on
