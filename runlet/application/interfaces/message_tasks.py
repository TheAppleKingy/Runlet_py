from typing import Optional


class MessageTask:
    resource: str
    task_name: Optional[str] = None

    def __init__(self, data: str):
        self.data = data


class SendMail(MessageTask):
    resource = "mail"


class SendCodeSolution(MessageTask):
    resource = "test_solutions"
    task_name = "test_solution"
