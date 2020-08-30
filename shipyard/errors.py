class NotFound(Exception):
    """Error used when no object is found."""

    pass


class AlreadyPresent(Exception):
    """Error used when there is an instance of an object is already present."""

    pass


class NotFeasible(Exception):
    """Error used when a given taskset's execution is not feasible."""

    pass


class MissingDevices(Exception):
    """
    Error used when a target node doesn't some of the devices required by a
    task.
    """

    pass
