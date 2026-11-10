-- SF-09 snowflake_get_login_history   (Phase 2)
-- Binds: :user_name, :days, :limit, :failures_only (boolean)
SELECT
    event_timestamp,
    event_type,
    is_success,
    error_code,
    error_message,
    reported_client_type,
    reported_client_version,
    first_authentication_factor,
    second_authentication_factor,
    client_ip                 -- returned to 'platform' scope only; dropped otherwise
FROM SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY
WHERE user_name = :user_name
  AND event_timestamp >= DATEADD('day', -:days, CURRENT_TIMESTAMP())
  AND (NOT :failures_only OR is_success = 'NO')
ORDER BY event_timestamp DESC
LIMIT :limit;
