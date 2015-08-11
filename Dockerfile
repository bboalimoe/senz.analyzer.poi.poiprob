FROM texastribune/supervisor

MAINTAINER jiaying.lu lujiaying93@foxmail.com


RUN pip install -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com numpy




RUN pip install -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com Cython
RUN apt-get update
RUN apt-get install -y python-scipy



WORKDIR /app
RUN mkdir ./leanEngine_app

ADD leanEngine_app ./leanEngine_app
ADD supervisor.conf /etc/supervisor/conf.d/
RUN pip install -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com -r ./leanEngine_app/requirements.txt
RUN pip install -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com gunicorn==19.1.1

EXPOSE 9010
