#!/bin/bash -x
export PATH=/radioco/radioco/configs/${ENVIRONMENT}/docker/scripts:$PATH

wait_for_postgres_server.sh
${POSTGRES} -tc "SELECT 1 FROM pg_database WHERE datname = '${POSTGRES_DB}'" | grep -q 1 || ${POSTGRES} -c "CREATE DATABASE ${POSTGRES_DB}"

${MANAGE_PY} migrate

/usr/sbin/sshd

# Keep container running 
tail -f /dev/null