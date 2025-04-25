FROM python:3.12-alpine AS builder
ARG APP_NAME=code2tutorials

LABEL org.opencontainers.image.authors="samin-irtiza" \
    description="A Dockerfile for building and running the ${APP_NAME} application" \
    version="1.0"

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt /app/

RUN apk add --no-cache git patchelf binutils && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install pyinstaller

COPY . /app

RUN pyinstaller --onefile --name $APP_NAME main.py

FROM alpine:latest
ARG APP_NAME=code2tutorials

LABEL org.opencontainers.image.authors="samin-irtiza" \
    description="A lightweight runtime image for the ${APP_NAME} application" \
    version="1.0"

WORKDIR /app

COPY --from=builder /app/dist /app/

RUN apk add --no-cache git

RUN chmod +x /app/$APP_NAME

ENV APP_NAME=${APP_NAME}

ENTRYPOINT ["/bin/sh", "-c", "/app/$APP_NAME"]
CMD ["--help"]