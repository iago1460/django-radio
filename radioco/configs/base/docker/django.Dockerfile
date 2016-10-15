FROM python:2.7


RUN apt-get update  && apt-get install -y --no-install-recommends \
    python-setuptools \
    python-pip \
    git-core \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools virtualenv

COPY tmp_requirements.txt requirements.txt
RUN pip install -r requirements.txt
