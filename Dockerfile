FROM python:3.13-slim as build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /usr/app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project --python /usr/local/bin/python

FROM python:3.13-slim

RUN groupadd -g 999 webapp && \
    useradd -r -u 999 -g webapp webapp

WORKDIR /usr/app

# Ensuring we have proper permissions for the data directory
RUN mkdir -p /usr/app/data && chown -R webapp:webapp /usr/app

COPY --from=build /usr/app/.venv ./.venv
COPY --chown=webapp:webapp . .

USER webapp
ENV PATH="/usr/app/.venv/bin:$PATH"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/ping')"

CMD ["uvicorn", "app.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
