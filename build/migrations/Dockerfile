FROM python:3.13-alpine3.22

RUN apk add --no-cache curl netcat-openbsd

WORKDIR /migrations

COPY build/migrations/poetry.lock build/migrations/pyproject.toml ./

RUN pip install poetry
ENV PATH="/root/.local/bin:$PATH"

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

COPY ./src/infrastructure/db/tables ./src/infrastructure/db/tables
COPY ./src/infrastructure/configs.py ./src/infrastructure/configs.py
COPY ./build/migrations/alembic ./src/alembic
COPY ./build/migrations/alembic.ini ./src/alembic.ini
COPY ./src/domain ./src/domain