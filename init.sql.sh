#!/bin/bash
set -e

echo "PostgreSQL is up - executing command"

# Execute the init.sql script
psql -v ON_ERROR_STOP=1 \
--username "$POSTGRES_USER" \
--dbname "$POSTGRES_DB" \
--command """
    create schema if not exists ${APP_DB_SCHEMA}; \
    create extension if not exists \"uuid-ossp\"; \
    create user ${APP_DB_USER} with password '${APP_DB_PASS}'; \
    GRANT USAGE ON SCHEMA ${APP_DB_SCHEMA} TO ${APP_DB_USER}; \
    GRANT CREATE ON SCHEMA ${APP_DB_SCHEMA} TO ${APP_DB_USER}; \
    GRANT CREATE ON SCHEMA public TO ${APP_DB_USER}; \
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ${APP_DB_SCHEMA} TO ${APP_DB_USER}; \
    ALTER DEFAULT PRIVILEGES IN SCHEMA ${APP_DB_SCHEMA} GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${APP_DB_USER}; \
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ${APP_DB_SCHEMA} TO ${APP_DB_USER}; \
    ALTER DEFAULT PRIVILEGES IN SCHEMA ${APP_DB_SCHEMA} GRANT USAGE, SELECT ON SEQUENCES TO ${APP_DB_USER};\
    """