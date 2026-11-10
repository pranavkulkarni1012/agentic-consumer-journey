-- SF-05 snowflake_get_failed_queries
-- Binds: :user_name, :days (1-14), :limit (1-50); :table_like optional ('%ORDERS%')
-- Source lag: up to ~45 minutes (ACCOUNT_USAGE.QUERY_HISTORY)
SELECT
    query_id,
    start_time,
    end_time,
    user_name,
    role_name,
    secondary_role_stats,
    warehouse_name,
    database_name,
    schema_name,
    query_type,
    execution_status,
    error_code,
    error_message,
    LEFT(query_text, 4000) AS query_text,
    query_tag,
    session_id,
    total_elapsed_time
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE user_name = :user_name
  AND start_time >= DATEADD('day', -:days, CURRENT_TIMESTAMP())
  AND UPPER(execution_status) IN ('FAIL', 'INCIDENT')
  AND (:table_like IS NULL OR query_text ILIKE :table_like)
ORDER BY start_time DESC
LIMIT :limit;
-- Handler notes:
--  * query_text MUST pass through caa_core.redaction.redact_sql (string and numeric
--    literals replaced) before it leaves the handler. Return query_text_redacted only.
--  * Snowflake itself redacts the text of statements that failed with syntax errors
--    unless the account sets ENABLE_UNREDACTED_QUERY_SYNTAX_ERROR. Expect '<redacted>'.
--  * error_class is assigned in code from config/error-catalog.yaml.
--  * secondary_role_stats is a JSON string; parse to secondary_roles (list or 'ALL').
--  * For "it failed a minute ago" the row may not be here yet. Return freshness.lagged
--    and let the agent ask for the query id or wait (ADR-007).
