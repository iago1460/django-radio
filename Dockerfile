FROM python:2.7
MAINTAINER Iago Veloso Abalo "author@radioco.org"

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app
RUN pip install --no-cache-dir -r radio/configs/docker/requirements.txt
