#!/bin/bash -x
export PATH=/radioco/radioco/configs/${ENVIRONMENT}/docker/scripts:$PATH
${MANAGE_PY} migrate
${MANAGE_PY} runserver 0.0.0.0:8000