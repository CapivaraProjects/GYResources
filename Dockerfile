FROM debian:stretch

WORKDIR /root

ADD api ./api
ADD app.py ./app.py
ADD backupGreeneyes.sql ./backupGreeneyes.sql
ADD config.py ./config.py
ADD database ./database
ADD Dockerfile ./Dockerfile
ADD missingSQL.sql ./missingSQL.sql
ADD models ./models
ADD README.md ./README.md
ADD repository ./repository 
ADD requirements.txt ./requirements.txt
ADD tests ./tests
ADD thumb ./thumb
ADD tools ./tools

RUN apt-get update && \
        apt-get install python \
        python3 \
        python-dev \
        python3-dev \
        python-pip \
        python3-pip \
        git \
        build-essential \
        gcc \
        postgresql-9.5

RUN pip3 install -r requirements.txt

