import paramiko

from shipyard.task.model import Task
from shipyard.node.model import Node


def deploy_task(task_file, task_name: str, node: Node):
    """
    Sends a task to a certain node and makes it run.

    The given task file  is a `tar.gz` file containing the task's image and all
    the needed source files to build it.

    This function connects to the target node by SSH, sends the file,
    decompresses it, builds the image and runs the container. The original file
    is removed from the node after the fact and only the image and source files
    remain.
    """

    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(node.ip, username=node.ssh_user, password=node.ssh_pass)

        with ssh.open_sftp() as sftp:
            sftp.putfo(task_file,
                       f'/home/{node.ssh_user}/.shipyard/{task_name}.tar.gz')

        ssh.exec_command(
            f'tar -xzf /home/{node.ssh_user}/.shipyard/{task_name}.tar.gz -C /home/{node.ssh_user}/.shipyard')
        ssh.exec_command(
            f'rm -f /home/{node.ssh_user}/.shipyard/{task_name}.tar.gz')
        ssh.exec_command(
            f'docker build -t {task_name} /home/{node.ssh_user}/.shipyard/{task_name}')
        ssh.exec_command(
            f'docker run -d --cap-add=sys_nice --name={task_name} {task_name}')
