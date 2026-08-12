FROM python:3.12-slim AS builder
WORKDIR /build
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
COPY pyproject.toml ./
COPY app ./app
RUN python -m venv /opt/venv && /opt/venv/bin/pip install .

FROM python:3.12-slim AS runtime
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN groupadd --system fraudlens && useradd --system --gid fraudlens --home /app fraudlens
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=fraudlens:fraudlens alembic.ini ./
COPY --chown=fraudlens:fraudlens alembic ./alembic
COPY --chown=fraudlens:fraudlens config ./config
COPY --chown=fraudlens:fraudlens entrypoint.sh ./entrypoint.sh
RUN chmod 0555 ./entrypoint.sh
USER fraudlens
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
ENTRYPOINT ["./entrypoint.sh"]
