#!/bin/bash
set -e

# Modificar pg_hba.conf para permitir conexiones con password desde cualquier host
echo "host    all             all             0.0.0.0/0               md5" >> /var/lib/postgresql/data/pg_hba.conf
echo "host    all             all             ::/0                    md5" >> /var/lib/postgresql/data/pg_hba.conf

# Recargar configuración de PostgreSQL
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT pg_reload_conf();
EOSQL