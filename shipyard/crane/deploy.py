import paramiko

from shipyard.node.model import Node
from shipyard.node.model import Task


def deploy_task(task_file, task: Task, node: Node):
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
                       f'/home/{node.ssh_user}/.shipyard/{task.name}.tar.gz')

        ssh.exec_command(
            f'tar -xzf /home/{node.ssh_user}/.shipyard/{task.name}.tar.gz -C /home/{node.ssh_user}/.shipyard')
        ssh.exec_command(
            f'rm -f /home/{node.ssh_user}/.shipyard/{task.name}.tar.gz')
        _, stdout, _ = ssh.exec_command(
            f'docker build -t {task.name} /home/{node.ssh_user}/.shipyard/{task.name}')
        while not stdout.channel.exit_status_ready():
            pass

        capabilities = ['--cap-add=sys_nice'] + \
            [f'--cap-add={cap}' for cap in task.capabilities]
        devices = [f'--device={dev}' for dev in task.devices]
        ssh.exec_command(
            f'docker run -d {" ".join(capabilities)} {" ".join(devices)} --name={task.name} {task.name}')
