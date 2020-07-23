import socket

from typing import List

from marshmallow import ValidationError


def validate_ip(ip_str: str):
    try:
        socket.inet_aton(ip_str)
    except socket.error:
        raise ValidationError('Invalid IP address.')


def validate_devices(device_list: List[str]):
    for device in device_list:
        if not device.startswith('/dev/'):
            raise ValidationError('Invalid Linux device path.')
