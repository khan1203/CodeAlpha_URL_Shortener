FROM python:3.12-slim

# Install uv (fast Python package/project manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy dependency files first so Docker can cache the install layer
COPY pyproject.toml ./
COPY uv.lock* ./

# Install dependencies into a project-local virtual environment (.venv)
RUN uv sync --no-dev --no-install-project

# Now copy the rest of the application code
COPY app ./app

# Make sure the venv's binaries are on PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
