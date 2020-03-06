FROM python:3.6.10-buster

RUN apt-get update && apt-get install -yq --fix-missing --no-install-recommends \
    python3-setuptools \
    python3-pip \
    git-core \
    netcat \
    nodejs \
    npm \
    gettext \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

# Installing libraries

RUN npm install -g bower

# Install pip dependencies
RUN pip3 install --upgrade pip setuptools virtualenv

COPY .bowerrc bower.json /
RUN bower install

COPY requirements.txt /
RUN pip3 install -r requirements.txt

COPY ./ /radioco/

WORKDIR /radioco/