#!/bin/bash -x
cd /radioco && bower install && cd -

if !(psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -w -c "")
then
    echo "Postgres connection is unavailable, execution aborted"
    exit 1
fi

# Allow this command to crash if postgres is unavailable
${POSTGRES} -tc "SELECT 1 FROM pg_database WHERE datname = '${POSTGRES_DB}'" | grep -q 1 || ${POSTGRES} -c "CREATE DATABASE ${POSTGRES_DB}"
${MANAGE_PY} migrate