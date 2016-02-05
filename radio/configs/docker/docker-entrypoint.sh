#!/bin/sh
python radio/configs/docker/manage.py collectstatic --noinput
/usr/local/bin/gunicorn radio.configs.docker.wsgi:application -w 2 -b :8000