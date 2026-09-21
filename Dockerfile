# --- STAGE 1: Build Flet Web with uv ---
FROM python:3.12-slim AS builder

# Copy official uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global --add safe.directory '*'

ENV BOT_PAYLOAD=1

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen || uv sync

COPY . .

RUN uv run flet build web --yes

FROM nginx:alpine

COPY --from=builder /app/build/web /usr/share/nginx/html

RUN echo 'server { \
    listen 8000; \
    location / { \
        root /usr/share/nginx/html; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 8000
CMD ["nginx", "-g", "daemon off;"]
