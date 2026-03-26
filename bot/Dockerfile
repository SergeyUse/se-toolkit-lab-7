# Bot Dockerfile using uv for dependency management
# See: https://docs.astral.sh/uv/guides/integration/docker/

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/

# ---
# Stage 1: Build the application
# ---
FROM ${REGISTRY_PREFIX}astral/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Sync dependencies first (better layer caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=bot/uv.lock,target=uv.lock \
    --mount=type=bind,source=bot/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy bot source code
COPY bot /app/bot

# Sync again to include the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# ---
# Stage 2: Final runtime image
# ---
FROM ${REGISTRY_PREFIX}python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Create non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy application from builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Use non-root user
USER nonroot

WORKDIR /app/bot

# Run the bot
CMD ["python", "bot.py"]
