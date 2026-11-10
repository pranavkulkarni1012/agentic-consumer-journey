-- SF-08 snowflake_get_table_status
-- Binds: :db, :schema, :table
-- Returns live and recently dropped versions so drop/recreate is visible.
SELECT
    table_id,
    table_catalog,
    table_schema,
    table_name,
    table_type,
    is_iceberg,      -- VERIFY column availability in CAA-003
    table_owner,
    row_count,
    bytes,
    created,
    last_altered,
    deleted
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLES
WHERE table_catalog = :db
  AND table_schema  = :schema
  AND table_name    = :table
ORDER BY created DESC
LIMIT 5;
-- Handler notes:
--  * exists = first row has deleted IS NULL
--  * recreated_recently = a deleted version exists and the live version was created in
--    the last :recreate_window_days (config, default 14). Recreated tables lose grants
--    and policies unless they were recreated with COPY GRANTS and Immuta re-synced.
--  * Views are in ACCOUNT_USAGE.VIEWS; query it when no row is found here.
