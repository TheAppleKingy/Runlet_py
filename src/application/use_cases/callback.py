from src.application.dtos.callback import CodeRunCallbackDTO


class CodeRunCallbackUseCase:
    def __init__(self, problem_repo):
        self._problem_repo = problem_repo

    async def execute(self, dto: CodeRunCallbackDTO):
        pass
