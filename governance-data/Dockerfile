FROM python:3.12-alpine

RUN addgroup -S -g 10001 governance \
    && adduser -S -D -H -u 10001 -G governance governance

WORKDIR /app
COPY server.py /app/server.py

USER 10001:10001
EXPOSE 8081

ENTRYPOINT ["python", "/app/server.py"]
