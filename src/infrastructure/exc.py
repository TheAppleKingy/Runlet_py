from src.domain.exc import HandlingError


class InfrastructureError(HandlingError):
    def __init__(self, *args, status=500):
        super().__init__(*args, status=status)
