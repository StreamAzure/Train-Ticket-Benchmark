FROM openjdk:8-jre

RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

ADD ./target/ts-admin-user-service-1.0.jar /app/
ADD ./apache-skywalking-java-agent-9.1.0.tgz /app/
ADD ./ca.pem /app/
ADD ./http-proxy-agent-1.3.5-dist.jar /app/

ENV SW_AGENT_NAME=ts-admin-user-service
ENV SW_AGENT_COLLECTOR_BACKEND_SERVICES=oap-server:11800
# 捕获的数据库语句显示具体参数
ENV SW_JDBC_TRACE_SQL_PARAMETERS=true
ENV SW_PLUGIN_FEIGN_COLLECT_REQUEST_BODY=true
ENV SW_PLUGIN_HTTPCLIENT_COLLECT_HTTP_PARAMS=true
ENV SW_PLUGIN_SPRINGMVC_COLLECT_HTTP_PARAMS=true
ENV JAVA_TOOL_OPTIONS "-javaagent:/app/skywalking-agent/skywalking-agent.jar -javaagent:/app/http-proxy-agent-1.3.5-dist.jar='interceptor|8080|/app/ca.pem'"
CMD ["java", "-Xmx200m",  "-jar", "/app/ts-admin-user-service-1.0.jar"]

EXPOSE 16115