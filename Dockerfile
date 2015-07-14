FROM python:2.7

MAINTAINER jiaying.lu lujiaying93@foxmail.com

RUN apt-get update 

RUN pip install Cython
RUN pip install numpy
RUN apt-get install -y python-scipy
RUN pip install scikit-learn
RUN pip install hmmlearn

WORKDIR /app
RUN mkdir ./leanEngine_app

ADD leanEngine_app ./leanEngine_app
RUN pip install -r ./leanEngine_app/requirements.txt

CMD python leanEngine_app/wsgi.py >/dev/null 2>&1 &

EXPOSE 9010
