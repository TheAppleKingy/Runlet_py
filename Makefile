include build/tests/.env.test

MIGRATION_COMPOSE=build/migrations/compose.yaml

DEV_COMPOSE=build/dev/compose.yaml

PROD_COMPOSE=build/prod/compose.yaml

TESTS_COMPOSE=build/tests/compose.yaml
TESTS_PATH=tests
INTEGRATION_TESTS_PATH=${TESTS_PATH}/test_integration
UNIT_TESTS_PATH=${TESTS_PATH}/test_unit


poetry.add:
	@poetry add ${dep}


poetry.rm:
	@poetry remove ${dep}

#-------------------------------------------------------------------------------------------------

runlet.dev.build:
	@docker compose -f ${DEV_COMPOSE} build


runlet.dev.start:
	@docker compose -f ${DEV_COMPOSE} up


runlet.dev.build.start:
	@docker compose -f ${DEV_COMPOSE} up --build

runlet.dev.down:
	@docker compose -f ${DEV_COMPOSE} down

#-------------------------------------------------------------------------------------------------

runlet.migrations.init:
	@cd build/migrations && alembic init -t async alembic


runlet.migrations.build:
	@docker compose -f ${MIGRATION_COMPOSE} build


runlet.migrations.new: runlet.migrations.build
	@docker compose -f ${MIGRATION_COMPOSE} run --rm migrations alembic revision --autogenerate -m ${msg}


runlet.migrations.up: runlet.migrations.build
	@docker compose -f ${MIGRATION_COMPOSE} run --rm migrations alembic upgrade head


runlet.migrations.down:
	@docker compose -f ${MIGRATION_COMPOSE} run --rm migrations alembic downgrade ${n}

#-------------------------------------------------------------------------------------------------

runlet.test.build:
	@docker compose -f ${TESTS_COMPOSE} build

runlet.test_db.start:
	@docker compose -f ${TESTS_COMPOSE} up -d test_db
	@until docker compose -f ${TESTS_COMPOSE} exec test_db pg_isready -U ${POSTGRES_USER}; do sleep 1; done


runlet.test.integration: runlet.test.build runlet.start.test_db
	@docker compose -f ${TESTS_COMPOSE} run --rm test_app pytest -v ${INTEGRATION_TESTS_PATH}; docker compose -f ${TESTS_COMPOSE} down

runlet.test.unit: runlet.test.build
	@docker compose -f ${TESTS_COMPOSE} run --rm test_app pytest -v ${UNIT_TESTS_PATH}

runlet.test.full: runlet.test.build runlet.start.test_db
	@docker compose -f ${TESTS_COMPOSE} run --rm test_app pytest -v ${TESTS_PATH}; docker compose -f ${TESTS_COMPOSE} down