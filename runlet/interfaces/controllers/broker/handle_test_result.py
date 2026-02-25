from ploomby.registry import HandlersRegistry

from runlet.application.dtos.callback import ResultDTO
from runlet.application.interactors.callback import HandleTestResult
from runlet.container import container

reg = HandlersRegistry()


@reg.register()
async def handle_test_result(dto: ResultDTO):
    async with container() as scoped:
        interactor = await scoped.get(HandleTestResult)
    await interactor(dto)
