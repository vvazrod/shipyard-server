import paramiko

from shipyard.node.model import Node


def remove_task(task_name: str, node: Node):
    """
    Removes a task from a given node.

    This function connects to the node by SSH, removes the task's container and
    source files.
    """

    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(node.ip, username=node.ssh_user, password=node.ssh_pass)

        ssh.exec_command(f'docker rm -f {task_name}')
        ssh.exec_command(f'rm -rf /home/{node.ssh_user}/.shipyard/{task_name}')
