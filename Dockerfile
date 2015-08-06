FROM texastribune/supervisor

MAINTAINER jiaying.lu lujiaying93@foxmail.com

#RUN apt-get update 
#RUN easy_install -U pip

#RUN apt-get install -y wget
#WORKDIR /
#RUN wget https://pypi.python.org/packages/source/p/pip/pip-0.7.1.tar.gz#md5=420c83ad67bdcb542f772eb64392cce6
#RUN pip install -U -i http://pypi.douban.com/simple/ pip 
RUN pip install -i http://pypi.douban.com/simple/  numpy

#RUN wget https://pypi.python.org/packages/source/p/pip/pip-0.7.1.tar.gz#md5=420c83ad67bdcb542f772eb64392cce6
#WORKDIR /
#RUN wget http://cython.org/release/Cython-0.22.1.tar.gz
#RUN tar -zxvf Cython-0.22.1.tar.gz
#RUN cd / && ls -a
#WORKDIR  /Cython-0.22.1
#RUN pwd
#RUN ls
#RUN python setup.py install


#RUN pip install --no-cache-dir  Cython
#RUN pip install --no-cache-dir numpy





#RUN apt-get update

#RUN apt-get install -y python-numpy
#WORKDIR /
#RUN wget https://github.com/numpy/numpy/archive/v1.9.2.tar.gz
#RUN tar -zxvf v1.9.2.tar.gz
#RUN ls
#RUN cd numpy-1.9.2  && python setup.py install
RUN pip install -i http://pypi.douban.com/simple/ Cython
#RUN pip install -i http://pypi.douban.com/simple/ scipy
RUN apt-get update
RUN apt-get install -y python-scipy

#WORDDIR /
#RUN wget https://pypi.python.org/packages/source/s/scikit-learn/scikit-learn-0.15.2.tar.gz
#RUN tar -zvxf scikit-learn-0.15.2.tar.gz
#WORKDIR /scikit-learn-0.15.2
#RUN python setup.py install 

#RUN pip install --no-cache-dir scikit-learn
#RUN pip install --no-cache-dir hmmlearn

WORKDIR /app
RUN mkdir ./leanEngine_app

ADD leanEngine_app ./leanEngine_app
ADD supervisor.conf /etc/supervisor/conf.d/
RUN pip install -i http://pypi.douban.com/simple/ -r ./leanEngine_app/requirements.txt

EXPOSE 9010
