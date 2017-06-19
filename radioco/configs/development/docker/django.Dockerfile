FROM python:2.7


# Installing libraries

RUN apt-get update  && apt-get install -y --no-install-recommends \
    python-setuptools \
    python-pip \
    git-core \
    nodejs-legacy \
    npm \
    postgresql-client \
    openssh-server \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

RUN npm install -g bower


# Setting up SSHD

RUN mkdir -p /var/run/sshd /root/.ssh
COPY id_rsa.pub /root/.ssh/id_rsa.pub

RUN cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys \
&& echo "KexAlgorithms diffie-hellman-group1-sha1" >> /etc/ssh/sshd_config


# Install pip dependencies

RUN pip install --upgrade pip setuptools virtualenv

ADD tmp_requirements.txt requirements.txt
RUN pip install -r requirements.txt
