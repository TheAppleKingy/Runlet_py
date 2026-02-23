from ploomby.registry import HandlersRegistry

from src.application.dtos.callback import ResultDTO
from src.application.use_cases.callback import HandleTestResultUseCase
from src.container import container

reg = HandlersRegistry()


@reg.register()
async def handle_test_result(dto: ResultDTO):
    async with container() as scoped:
        use_case = await scoped.get(HandleTestResultUseCase)
    await use_case.execute(dto)
