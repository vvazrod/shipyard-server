import docker

from shipyard.node.model import Node


def remove_task(task_name: str, node: Node):
    """
    Removes a task from a given node.

    This function connects to the node's Docker server and removes both the
    task's container and its image.
    """

    client = docker.DockerClient(base_url=f'ssh://{node.ssh_user}@{node.ip}')
    client.containers.get(task_name).remove(force=True)
    client.images.remove(image=task_name)
    client.close()
