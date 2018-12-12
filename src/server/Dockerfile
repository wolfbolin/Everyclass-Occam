FROM python:3.7.1-slim-stretch
MAINTAINER WolfBolin.com

WORKDIR /www/wwwroot/api-server

RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list \
	&& apt-get update \
	&& apt-get install wget unzip -y \
	&& pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com pipenv

COPY . /www/wwwroot/api-server

RUN pipenv sync

EXPOSE 80

CMD ['pipenv', 'run', 'python', 'app.py']
