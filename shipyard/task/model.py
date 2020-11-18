"""
The task model.
"""

from dataclasses import field
from typing import ClassVar, List, Optional, Type

from marshmallow import Schema
from marshmallow_dataclass import NewType, dataclass
from shipyard.fields import ObjectId
from shipyard.validators import validate_devices

objectid = NewType('objectid', str, ObjectId)


@dataclass(order=True)
class Task:
    """A real-time task that can be deployed as a container to a node."""

    _id: Optional[objectid] = field(metadata={'required': False})
    file_id: Optional[objectid] = field(metadata={'required': False})
    name: str
    runtime: int
    deadline: int
    period: int
    devices: List[str] = field(default_factory=lambda: [], metadata={
        'required': False,
        'validate': validate_devices
    })
    capabilities: List[str] = field(default_factory=lambda: [], metadata={
        'required': False
    })

    Schema: ClassVar[Type[Schema]] = Schema
