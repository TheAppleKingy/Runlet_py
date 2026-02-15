from src.domain.entities import Attempt, Module, User, Tag

from .dtos import ProblemWithRateInfoDTO, ModuleWithRateInfoDTO


def student_problems_info(attempts: list[Attempt], modules: list[Module]):
    module_map = {module.id: ModuleWithRateInfoDTO(name=module.name, order=module.order) for module in modules}
    for attempt in attempts:
        presented = module_map[attempt.problem.module_id]
        presented.problems.append(ProblemWithRateInfoDTO(id=attempt.problem_id,
                                  name=attempt.problem.name, tests_passed=attempt.tests_passed))
    return list(module_map.values())
