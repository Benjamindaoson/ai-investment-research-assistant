FROM eclipse-temurin:21-jre

WORKDIR /app

COPY target/stock-mcp-1.0-SNAPSHOT.jar app.jar
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

RUN chmod +x /app/docker-entrypoint.sh

ENV SPRING_PROFILES_ACTIVE=prod
ENV MCP_SERVER_PORT=7070

EXPOSE 7070

ENTRYPOINT ["/app/docker-entrypoint.sh"]
