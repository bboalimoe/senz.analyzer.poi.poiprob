FROM ubuntu

MAINTAINER jiaying.lu lujiaying93@foxmail.com

RUN apt-get update && apt-get -y install python-numpy python-scipy python-pip

WORKDIR /app
RUN mkdir ./leanEngine_app

ADD leanEngine_app ./leanEngine_app
RUN pip install -r ./leanEngine_app/requirements.txt