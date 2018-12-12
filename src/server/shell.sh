#!/bin/bash
# 自动完成测试代码更新部署
true
&& rm update.zip Everyclass-Occam-update -rf \
&& wget https://github.com/wolfbolin/Everyclass-Occam/archive/update.zip \
&& unzip update.zip \
&& cp config.py Everyclass-Occam-update/src/server/util/config.py \
&& cd Everyclass-Occam-update/src \
&& docker build -t everyclass/api:latest -f server/Dockerfile server \
&& docker stop api-server-v1 \
&& docker rm api-server-v1 \
&& docker run -d -p 25601:80 -v server:/www/wwwroot/api-server --name api-server-v1 everyclass/api