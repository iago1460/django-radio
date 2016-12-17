#!/bin/bash -x
cd /radioco && bower install && cd -

if !(psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -w -c "")
then
    echo "Postgres connection is unavailable, execution aborted"
    exit 1
fi

${POSTGRES} -tc "SELECT 1 FROM pg_database WHERE datname = '${POSTGRES_DB}'" | grep -q 1 || ${POSTGRES} -c "CREATE DATABASE ${POSTGRES_DB}"
${MANAGE_PY} collectstatic --noinput
${MANAGE_PY} migrate --noinput
