"""
Custom marshmallow validators.
"""

import socket
from typing import List

from marshmallow import ValidationError


def validate_ip(ip_str: str):
    """Check if the given string is a valid IPv4 address."""

    try:
        socket.inet_aton(ip_str)
    except socket.error:
        raise ValidationError('Invalid IP address.')


def validate_devices(device_list: List[str]):
    """Check if the given strings are valid device file paths."""

    for device in device_list:
        if not device.startswith('/dev/'):
            raise ValidationError('Invalid Linux device path.')
