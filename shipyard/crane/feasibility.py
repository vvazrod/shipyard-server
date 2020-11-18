"""
Feasibility checking algorithm.
"""

from typing import List

from shipyard.task.model import Task


def check_feasibility(tasks: List[Task], cpu_cores: int) -> bool:
    """
    Checks if the given taskset is feasible. This comprobation is based on the
    tasks' CPU utilization.

    If the tasks can be accomplished with the specified time restrictions,
    returns `True`. If not, returns `False`.
    """

    utilization = 0.0
    for task in tasks:
        utilization += task.runtime / min(task.deadline, task.period)

    if utilization <= 1 * cpu_cores:
        return True
    return False
