FROM eclipse-temurin:21-jre

WORKDIR /app

COPY target/stock-web-1.0-SNAPSHOT.jar app.jar
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

RUN chmod +x /app/docker-entrypoint.sh

ENV SPRING_PROFILES_ACTIVE=prod
ENV SERVER_PORT=6060

EXPOSE 6060

ENTRYPOINT ["/app/docker-entrypoint.sh"]
