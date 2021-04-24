FROM ubuntu

RUN apt-get update && apt-get upgrade
RUN apt-get install -y \
    python3 \
    python3-pip

ADD . /web_monitor/
WORKDIR /web_monitor/
RUN pip3 install -r requirements.txt