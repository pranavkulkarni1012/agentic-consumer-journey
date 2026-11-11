-- =============================================================================
-- Consumer Access Assistant (CAA) - Snowflake service identity setup
-- Run once per account by a security administrator. Review with the Snowflake
-- platform owner before running. Names are suggestions; align to your standards.
--
-- Principle: metadata only. This role gets NO privileges on data-mesh tables.
-- The view-to-database-role mapping below follows Snowflake's "SNOWFLAKE database roles"
-- documentation (checked November 2026). VERIFY in spike CAA-003 that every SQL file in
-- this folder runs under this role in your account. If one does not, prefer adding the
-- single missing database role over IMPORTED PRIVILEGES on the SNOWFLAKE database
-- (broader; record the exception).
-- =============================================================================

USE ROLE SECURITYADMIN;

CREATE ROLE IF NOT EXISTS CAA_DIAG_READER
  COMMENT = 'Consumer Access Assistant: read-only access to account metadata and usage views';

-- SNOWFLAKE database roles can only be granted by ACCOUNTADMIN (or a role that has been
-- given that ability). This is the one step that needs it.
USE ROLE ACCOUNTADMIN;

-- QUERY_HISTORY, ACCESS_HISTORY, POLICY_REFERENCES, TAG_REFERENCES
GRANT DATABASE ROLE SNOWFLAKE.GOVERNANCE_VIEWER TO ROLE CAA_DIAG_READER;
-- USERS, LOGIN_HISTORY, GRANTS_TO_USERS, GRANTS_TO_ROLES
GRANT DATABASE ROLE SNOWFLAKE.SECURITY_VIEWER   TO ROLE CAA_DIAG_READER;
-- TABLES, VIEWS, COLUMNS
GRANT DATABASE ROLE SNOWFLAKE.OBJECT_VIEWER     TO ROLE CAA_DIAG_READER;
-- USAGE_VIEWER is deliberately NOT granted: no Phase 1 or Phase 2 query in this folder
-- needs it. Add it only if a later tool reads a usage view, and record why.

USE ROLE SYSADMIN;

CREATE WAREHOUSE IF NOT EXISTS CAA_DIAG_WH
  WAREHOUSE_SIZE = XSMALL
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  STATEMENT_TIMEOUT_IN_SECONDS = 60
  COMMENT = 'Consumer Access Assistant diagnostics. Metadata queries only.';

GRANT USAGE ON WAREHOUSE CAA_DIAG_WH TO ROLE CAA_DIAG_READER;

USE ROLE SECURITYADMIN;

-- Key-pair service user. Public key is supplied by the CAA deployment pipeline;
-- the private key lives only in AWS Secrets Manager.
CREATE USER IF NOT EXISTS CAA_DIAG_SVC
  TYPE = SERVICE
  DEFAULT_ROLE = CAA_DIAG_READER
  DEFAULT_WAREHOUSE = CAA_DIAG_WH
  RSA_PUBLIC_KEY = '<PUBLIC_KEY_PEM_BODY>'
  COMMENT = 'Consumer Access Assistant service user (key-pair, no password)';

GRANT ROLE CAA_DIAG_READER TO USER CAA_DIAG_SVC;

-- Restrict the service user to the CAA egress addresses or PrivateLink endpoint.
-- CREATE NETWORK POLICY CAA_DIAG_NP ALLOWED_IP_LIST = ('<nat-egress-cidr>');
-- ALTER USER CAA_DIAG_SVC SET NETWORK_POLICY = CAA_DIAG_NP;

-- OPTIONAL (only if config/rls-models.yaml uses lookup-table row policies):
-- read access to the entitlement mapping table(s). These hold who-may-see-what,
-- not business data. Grant per table, never per schema.
-- GRANT USAGE ON DATABASE <GOV_DB> TO ROLE CAA_DIAG_READER;
-- GRANT USAGE ON SCHEMA <GOV_DB>.<ENTITLEMENT_SCHEMA> TO ROLE CAA_DIAG_READER;
-- GRANT SELECT ON TABLE <GOV_DB>.<ENTITLEMENT_SCHEMA>.<USER_ACCOUNT_MAP> TO ROLE CAA_DIAG_READER;

-- OPTIONAL (Phase 2, SF-11 Iceberg health): the SYSTEM$ functions and SHOW commands
-- need privileges on the specific external volumes / tables. Decide in ADR-007.
