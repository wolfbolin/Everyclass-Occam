FROM python:3.7.1-slim-stretch
MAINTAINER WolfBolin.com

WORKDIR /www/wwwroot/api-server

RUN apt-get update \
	&& apt-get install wget unzip -y \
	&& pip install pipenv \
	&& pipenv sync \
	&& pipenv run python app.py

EXPOSE 80
