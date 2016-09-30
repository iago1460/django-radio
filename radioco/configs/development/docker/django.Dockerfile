FROM python:2.7


RUN apt-get update  && apt-get install -y --no-install-recommends \
    postgresql-client \
    python-setuptools \
    python-pip \
    git-core \
    openssh-server \
&& apt-get clean && rm -rf /var/lib/apt/lists/*


RUN mkdir -p /var/run/sshd /root/.ssh

COPY id_rsa.pub /root/.ssh/id_rsa.pub

RUN cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys \
&& echo "KexAlgorithms diffie-hellman-group1-sha1" >> /etc/ssh/sshd_config


RUN pip install --upgrade pip setuptools virtualenv

COPY tmp_requirements.txt requirements.txt
RUN pip install -r requirements.txt
