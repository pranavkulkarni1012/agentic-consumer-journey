-- SF-10 snowflake_get_access_history   (Phase 2)
-- Binds: :user_name, :fqn ('DB.SCHEMA.TABLE'), :days
-- Source lag: up to ~3 hours. Enterprise Edition feature.
WITH hits AS (
    SELECT ah.query_id, ah.query_start_time
    FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY ah,
         LATERAL FLATTEN(input => ah.base_objects_accessed) obj
    WHERE ah.user_name = :user_name
      AND ah.query_start_time >= DATEADD('day', -:days, CURRENT_TIMESTAMP())
      AND obj.value:"objectName"::string = :fqn
)
SELECT
    MAX(h.query_start_time)                       AS last_success_at,
    MAX_BY(qh.role_name, h.query_start_time)      AS last_success_role,
    COUNT(DISTINCT h.query_id)                    AS access_count
FROM hits h
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY qh
       ON qh.query_id = h.query_id
      AND qh.start_time >= DATEADD('day', -:days - 1, CURRENT_TIMESTAMP());
