FROM wendelhime/basic:latest

RUN apt-get update && \
        apt-get install -y postgresql

WORKDIR /root/git
RUN git clone https://github.com/CapivaraProjects/GYResources && \
        pip3 install -r GYResources/requirements.txt

