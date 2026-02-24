from ploomby.registry import HandlersRegistry

from src.application.dtos.callback import ResultDTO
from src.application.interactors.callback import HandleTestResult
from src.container import container

reg = HandlersRegistry()


@reg.register()
async def handle_test_result(dto: ResultDTO):
    async with container() as scoped:
        interactor = await scoped.get(HandleTestResult)
    await interactor(dto)
