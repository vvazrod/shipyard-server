import docker

from shipyard.node.model import Node
from shipyard.node.model import Task


def deploy_task(task_file, task: Task, node: Node):
    """
    Sends a task to a certain node and makes it run.

    The given task file is a `tar.gz` file containing the task's image and all
    the needed source files to build it.

    This function connects to the node's Docker server by SSH, builds the image
    using the custom context contained in the tar gile and then runs the
    container.
    """

    client = docker.DockerClient(base_url=f'ssh://{node.ssh_user}@{node.ip}')
    client.images.build(
        tag=task.name,
        fileobj=task_file,
        custom_context=True,
        encoding='gzip'
    )
    client.containers.run(
        task.name,
        name=task.name,
        detach=True,
        cap_add=['SYS_NICE'] + task.capabilities,
        devices=task.devices,
        environment={
            'TASK_RUNTIME': task.runtime,
            'TASK_DEADLINE': task.deadline,
            'TASK_PERIOD': task.period
        }
    )
    client.close()
