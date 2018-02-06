# GYResources [![Build Status](https://travis-ci.org/CapivaraProjects/GYResources.svg?branch=master)](https://travis-ci.org/CapivaraProjects/GYResources)
This repository is dedicated to turn available green eyes resources in a API and website project

# Dependences

Install PostgreSQL:

```zsh
sudo apt update && \
  sudo apt install postgresql \
    python3-dev
    python3-pip
```

Enter in postgresql:
```zsh
psql template1 -U postgres
```

Create your user:
```
CREATE ROLE capivara LOGIN SUPERUSER INHERIT CREATEDB LOGIN;
ALTER USER capivara WITH PASSWORD 'test';
CREATE DATABASE green_eyes;
```

Add the following line in /etc/postgresql/9.5/main/pg_hba.conf:
```
local   all             capivara                                     md5
```
and restart postgresql:

```
sudo /etc/init.d/postgresql restart
```

Clone this repository, enter and execute:

```zsh
psql green_eyes -U capivara <  	backupGreeneyes.sql
```

Install dependences from project:
```zsh
pip3 install -r requirements.txt
```

# Running
```zsh
python3 app.py
```

# Docker
You can use docker for development using:
```zsh
docker run \
    -v /dir/to/GYResources:/root/git/GYResources \
    -p 8888:8888 \
    --net=host \
    -it \
    --rm wendelhime/gyresources /usr/bin/zsh
```
