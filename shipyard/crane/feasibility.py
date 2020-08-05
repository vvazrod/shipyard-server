from typing import List

from shipyard.task.model import Task


def check_feasibility(tasks: List[Task]) -> bool:
    utilization = 0.0
    for task in tasks:
        utilization += task.runtime / min(task.deadline, task.period)

    if utilization <= 1:
        return True
    return False
