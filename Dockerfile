# Generic Dockerfile template
# Jenkins can build this as-is for Python repos and teams can adapt the
# placeholders for Node.js or C++ projects when needed.

ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE}

WORKDIR /app

COPY . /app

# Optional build command:
# docker build --build-arg BUILD_COMMAND="npm ci && npm run build" ...
ARG BUILD_COMMAND=""
RUN if [ -n "$BUILD_COMMAND" ]; then sh -c "$BUILD_COMMAND"; fi

# Optional app port:
ARG APP_PORT=5000
EXPOSE ${APP_PORT}

# Default Python startup command.
# Override at build time for Node/C++ apps:
# docker build --build-arg START_COMMAND="node server.js" ...
ARG START_COMMAND="gunicorn --bind 0.0.0.0:5000 app:app"
ENV START_COMMAND=${START_COMMAND}

CMD ["sh", "-c", "$START_COMMAND"]
