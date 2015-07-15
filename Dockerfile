FROM texastribune/supervisor

MAINTAINER jiaying.lu lujiaying93@foxmail.com

#RUN apt-get update 
#RUN easy_install -U pip
RUN apt-get install -y wget
WORKDIR /
RUN wget https://pypi.python.org/packages/source/p/pip/pip-0.7.1.tar.gz#md5=420c83ad67bdcb542f772eb64392cce6
RUN tar -zxvf pip-0.7.1.tar.gz
RUN ls
WORKDIR  /pip-0.7.1
RUN pwd
RUN python setup.py install

RUN pip install --no-cache-dir  Cython
RUN pip install --no-cache-dir numpy
RUN apt-get install -y python-scipy
RUN pip install --no-cache-dir scikit-learn
RUN pip install --no-cache-dir hmmlearn

WORKDIR /app
RUN mkdir ./leanEngine_app

ADD leanEngine_app ./leanEngine_app
RUN pip install -r --no-cache-dir ./leanEngine_app/requirements.txt

#CMD python leanEngine_app/wsgi.py >/dev/null 2>&1 &

EXPOSE 9010
