
# Train Ticket：A Benchmark Microservice System
# <img src="./image/logo.png">
The project is a train ticket booking system based on microservice architecture which contains 45 microservices. The programming languages and frameworks it used are as below.
- Java - Spring Boot, Spring Cloud
- Node.js - Express (ts-ticket-office-service)
- Python - Django (ts-voucher-service, ts-avatar-service)
- Go - Webgo (ts-news-service)
- DB - Mongo、MySQL

## 全局配置
- 各 MySQL 实例的 root 密码：root；MySQL中的所使用的数据库名均为 ts


## 更改
- 更新 docker-compose 文件，使重构后的 TrainTicket 能以 Docker Compose 方式部署
- 统一修改源码中各服务的nacos、数据库等配置，修复所有配置不当所导致的容器启动失败的bug
- 观察到因容器启动顺序导致的问题
    - 如果微服务容器比nacos先启动，其与nacos连接会失败并使容器自动退出
    - 如果前端服务ts-ui-dashboard容器在ts-gateway-service服务完全启动之前启动，会因反向代理找不到ts-gateway-service而导致前端请求返回 502 badgateway（表现之一为验证码图片无法显示）
    - 暂时的解决方案：拆分为 3 个docker-compose文件，手动按顺序依次部署，其中
        - docker-compose-base-1.yml：Nacos + 所有的MySQL容器
        - docker-compose-base-2.yml：所有的微服务（除ts-ui-dashboard外）
        - docker-compose-base-3.yml：ts-ui-dashboard 容器

## 运行
### 源码编译&镜像构建
```shell
python build_upload_image.py
```
该脚本会自动执行 mvn 编译、jar打包及 docker 镜像构建，注意在其中指定镜像名前缀及版本号
### 通过 docker-compose 部署
- SkyWalking 版，已整合 SkyWalking 链路追踪
    ```shell
    docker-compose -f deployment/docker-compose-manifests/docker-compose-skywalking-1.yml up -d
    # 查看日志，确保MySQL容器、Nacos、OAP-Server均完全启动并能提供服务后，再执行下一步
    docker-compose -f deployment/docker-compose-manifests/docker-compose-skywalking-2.yml up -d
    # 查看日志，确保ts-gateway-service完全启动并能提供服务后（即日志输出 Started GatewayApplication in ** seconds），再执行下一步
    docker-compose -f deployment/docker-compose-manifests/docker-compose-skywalking-3.yml up -d
    ```
    - 访问 [http://localhost:8080/client_login.html](http://localhost:8080/client_login.html)，若所有容器均正常运行且页面中验证码图片可以显示，则部署成功。
    - 访问 SkyWalking UI：[http://localhost:8090/general](http://localhost:8090/general)

## 自动请求脚本
Clone 自 [train-ticket-auto-query](https://github.com/FudanSELab/train-ticket-auto-query)

已完成的更新：
- 修正请求脚本中错误的key: `startingPlace` → `startPlace`。该错误会导致所有对路径/travelservice及/travelplan的Python请求失败