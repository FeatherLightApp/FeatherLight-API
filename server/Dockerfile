FROM python:3.8-slim-buster

ENV PROD_ENV=FALSE \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 

# System deps:
RUN pip install "poetry"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$PROD_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY featherlight /app/featherlight/

COPY tests /app/tests

CMD [ "sh", "-c", "poetry run compile && cd featherlight && python -m uvicorn main:APP --host 0.0.0.0 --port 5001 --log-level info --reload --reload-dir /app/featherlight"]