#!/bin/bash -x
cd /radioco && bower install && cd -
${MANAGE_PY} migrate