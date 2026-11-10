-- SF-06 snowflake_get_query_details
-- Binds: :query_id
-- Two statements; the handler merges them. ACCESS_HISTORY lags up to ~3 hours and has
-- no row for queries that failed before accessing objects.
SELECT
    query_id, start_time, end_time, user_name, role_name, secondary_role_stats,
    warehouse_name, database_name, schema_name, query_type, execution_status,
    error_code, error_message, LEFT(query_text, 4000) AS query_text, session_id
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE query_id = :query_id
  AND start_time >= DATEADD('day', -30, CURRENT_TIMESTAMP());

SELECT
    query_id,
    direct_objects_accessed,
    base_objects_accessed,
    policies_referenced
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
WHERE query_id = :query_id
  AND query_start_time >= DATEADD('day', -30, CURRENT_TIMESTAMP());
-- Authorisation: the handler compares user_name with the resolved subject. A 'self'
-- requester may only fetch their own query ids; otherwise return status "denied".
