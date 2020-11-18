"""
The node model.
"""

from dataclasses import field
from typing import ClassVar, List, Optional, Type

from marshmallow import Schema
from marshmallow_dataclass import NewType, dataclass
from shipyard.fields import ObjectId
from shipyard.task.model import Task
from shipyard.validators import validate_devices, validate_ip

objectid = NewType('objectid', str, ObjectId)


@dataclass(order=True)
class Node:
    """A node is a device where tasks can be deployed."""

    _id: Optional[objectid] = field(metadata={'required': False})
    name: str
    ip: str = field(metadata={'validate': validate_ip})
    cpu: Optional[str] = field(metadata={'required': False})
    cpu_arch: Optional[str] = field(metadata={'required': False})
    cpu_cores: int
    cpu_freq: Optional[int] = field(metadata={'required': False})
    ram: Optional[int] = field(metadata={'required': False})
    ssh_user: Optional[str] = field(metadata={'required': False})
    devices: List[str] = field(default_factory=lambda: [], metadata={
        'required': False,
        'validate': validate_devices
    })
    tasks: List[Task] = field(default_factory=lambda: [], metadata={
        'required': False
    })

    Schema: ClassVar[Type[Schema]] = Schema
