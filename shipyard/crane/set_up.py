"""
Node set up logic.
"""

import os

import paramiko


def set_up_node(address: str, ssh_user: str, ssh_pass: str):
    """
    Add node to known hosts and send the server's public key so the next
    connections can be made easily.
    """

    with paramiko.SSHClient() as ssh:
        if os.path.isfile('/root/.ssh/known_hosts'):
            ssh.load_host_keys('/root/.ssh/known_hosts')
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(address, username=ssh_user, password=ssh_pass)

        with ssh.open_sftp() as sftp:
            keys = sftp.file(f'/home/{ssh_user}/.ssh/authorized_keys', 'a')
            with open('/root/.ssh/id_rsa.pub', 'r') as public_key:
                keys.write(public_key.read())
