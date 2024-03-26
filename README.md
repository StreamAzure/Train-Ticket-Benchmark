
# Train Ticket：A Benchmark Microservice System
# <img src="./image/logo.png">
The project is a train ticket booking system based on microservice architecture which contains 41 microservices. The programming languages and frameworks it used are as below.
- Java - Spring Boot, Spring Cloud
- Node.js - Express
- Python - Django
- Go - Webgo
- DB - Mongo、MySQL

## 更改
- 更新 docker-compose 文件，使重构后的 TrainTicket 能以 Docker Compose 方式部署

## 运行
### 源码编译&镜像构建
```shell
python build_upload_image.py
```
该脚本会自动执行 mvn 编译、jar打包及 docker 镜像构建，注意在其中指定镜像名前缀及版本号
### 通过 docker-compose 部署
- Base 版，无链路追踪
```shell
docker-compose -f deployment/docker-compose-manifests/docker-compose-base.yml up -d
```
