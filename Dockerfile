FROM python:3.12-alpine AS builder
# Executable application name
ARG APP_NAME=code2tutorials

LABEL org.opencontainers.image.authors="samin-irtiza" \
      org.opencontainers.image.title="${APP_NAME} Builder" \
      org.opencontainers.image.description="Build layer for the ${APP_NAME} application, which generates tutorials from codebases." \
      org.opencontainers.image.version="1.0" \
      org.opencontainers.image.source="https://github.com/The-Pocket/Tutorial-Codebase-Knowledge"

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
# Executable application name
ARG APP_NAME=code2tutorials
LABEL org.opencontainers.image.authors="samin-irtiza" \
      org.opencontainers.image.title="${APP_NAME}" \
      org.opencontainers.image.description="Runtime layer for the ${APP_NAME} application, a CLI tool for generating tutorials from codebases." \
      org.opencontainers.image.version="1.0" \
      org.opencontainers.image.source="https://github.com/The-Pocket/Tutorial-Codebase-Knowledge"

WORKDIR /app

COPY --from=builder /app/dist /app/

RUN apk add --no-cache git

RUN chmod +x /app/$APP_NAME

# Change the entrypoint according to the executable application name. 
ENTRYPOINT ["/app/code2tutorials"]
CMD ["--help"]