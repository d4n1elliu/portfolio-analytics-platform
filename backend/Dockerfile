# Production image for the API. Build from the backend/ folder:
#   docker build -t portfolio-backend .
FROM python:3.12-slim

# Show log lines straight away, and do not write .pyc files into the image.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install the dependencies before copying the code, so Docker can reuse this
# step when only the code has changed. Only the packages the app needs to run
# are installed: no test or lint tools.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The app, plus what is needed to run migrations and the seed script inside
# the container. Settings come from environment variables, not a .env file.
COPY alembic.ini .
COPY alembic ./alembic
COPY scripts ./scripts
COPY app ./app

# Run as an ordinary user instead of root, so a bug in the app cannot change
# the files in the image.
RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 8000

# No --reload: that is for development only.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
