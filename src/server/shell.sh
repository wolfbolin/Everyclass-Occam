#!/bin/bash
# 自动完成测试代码更新部署
cd /root \
&& rm update.zip Everyclass-Occam-update -rf \
&& wget https://github.com/wolfbolin/Everyclass-Occam/archive/update.zip \
&& unzip update.zip \
&& cp config.py Everyclass-Occam-update/src/server/util/config.py \
&& cd Everyclass-Occam-update/src \
&& docker stop api-server-v1 \
&& docker rm api-server-v1 \
&& docker rmi everyclass/api:latest \
&& docker build -t everyclass/api:latest -f server/Dockerfile --no-cache server \
&& docker run -d -p 25600:80 --name api-server-v1 everyclass/api:latest \
&& docker start api-server-v1 \
&& docker ps