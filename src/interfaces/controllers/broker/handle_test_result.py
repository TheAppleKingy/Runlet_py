from ploomby.registry import HandlersRegistry

from src.application.dtos.callback import ResultDTO

from src.logger import logger

reg = HandlersRegistry()


@reg.register()
async def handle_test_result(dto: ResultDTO):
    logger.critical(f"{dto}")
