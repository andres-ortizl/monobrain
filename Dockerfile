FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
RUN uv sync --all-extras

# command is set per-service in docker-compose.yml
EXPOSE 8000 8001
