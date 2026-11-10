-- SF-07 snowflake_get_table_policies
-- Binds: :db, :schema, :table
-- Source lag: up to ~2 hours (ACCOUNT_USAGE.POLICY_REFERENCES)
SELECT
    policy_db,
    policy_schema,
    policy_name,
    policy_kind,            -- ROW_ACCESS_POLICY | MASKING_POLICY | ...
    ref_entity_domain,
    ref_column_name,        -- set for masking policies
    ref_arg_column_names,   -- set for row access policies
    policy_status
FROM SNOWFLAKE.ACCOUNT_USAGE.POLICY_REFERENCES
WHERE ref_database_name = :db
  AND ref_schema_name   = :schema
  AND ref_entity_name   = :table
ORDER BY policy_kind, ref_column_name;
-- Handler notes: immuta_managed = policy_db equals the Immuta database configured for
-- the integration (config: immuta.snowflake_database, default 'IMMUTA').
-- An Immuta data source with data policies but no rows here = enforcement gap (ENF-003).
