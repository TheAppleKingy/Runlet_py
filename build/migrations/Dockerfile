FROM python:3.13-alpine3.22

RUN apk add --no-cache curl netcat-openbsd

WORKDIR /migrations

COPY build/migrations/poetry.lock build/migrations/pyproject.toml ./

RUN pip install poetry
ENV PATH="/root/.local/bin:$PATH"

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

COPY ./runlet/infrastructure/db/tables ./runlet/infrastructure/db/tables
COPY ./runlet/infrastructure/configs.py ./runlet/infrastructure/configs.py
COPY ./build/migrations/alembic ./runlet/alembic
COPY ./build/migrations/alembic.ini ./runlet/alembic.ini
COPY ./runlet/domain ./runlet/domain