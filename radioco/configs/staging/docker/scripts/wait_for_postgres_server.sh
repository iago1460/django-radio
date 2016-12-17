#!/bin/bash -x
while ! $(psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -w -c ""); do sleep 1; done
