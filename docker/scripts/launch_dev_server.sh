#!/bin/bash -x

script_full_path=$(dirname "$0")
$script_full_path/wait_for.sh postgres 5432

rm -rf /radioco/radioco/apps/radioco/static/bower
mv -f /tmp_bower /radioco/radioco/apps/radioco/static/bower
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000