FROM python:3.7.1-slim-stretch
MAINTAINER WolfBolin.com

WORKDIR /www/wwwroot

RUN apt-get update \
	&& apt-get install wget unzip -y \
	&& pip install pipenv \
	&& wget https://github.com/wolfbolin/Everyclass-Occam/archive/update.zip \
	&& unzip update.zip \
	&& cp Everyclass-Occam-update/src/server /www/wwwroot/api-server \
	&& cp config.py api-server/util/config.py \
	&& rm Everyclass-Occam-update update.zip -rf \

RUN cd api-server \
	&& pipenv sync \
	&& pipenv run python app.py \