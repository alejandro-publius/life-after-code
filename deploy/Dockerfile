# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm@sha256:9901e0a8d75037d8242ed43155cbcb2d1f61be1356383d8054afb59fd50e39c4

# Change this one line to the real folder containing main.py and requirements.txt.
ARG APP_DIR=deploy/hello
ARG CI_COMMIT_SHORT_SHA=local
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080 CI_COMMIT_SHORT_SHA=${CI_COMMIT_SHORT_SHA}
WORKDIR /app
COPY ${APP_DIR}/requirements.txt /tmp/requirements.txt
# The optional certificate is for this managed workspace, not a deployed secret.
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    pip install --no-cache-dir --require-hashes -r /tmp/requirements.txt
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid 10001 --no-create-home app
COPY --chown=10001:10001 ${APP_DIR}/ /app/
USER 10001:10001
EXPOSE 8080
CMD ["sh", "-c", "exec python -m uvicorn main:app --host 0.0.0.0 --port \"${PORT:-8080}\" --workers 1 --no-access-log"]
