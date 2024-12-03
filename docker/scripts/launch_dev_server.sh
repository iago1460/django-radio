#!/bin/bash -x

script_full_path=$(dirname "$0")
$script_full_path/wait_for.sh postgres 5432

TARGET_DIR="/radioco/radioco/apps/radioco/static/bower"

if [ -d "$TARGET_DIR" ]; then
  rm -rf "$TARGET_DIR"
fi

mv -f /tmp_bower "$TARGET_DIR"

python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000