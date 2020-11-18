"""
Custom marshmallow fields.
"""

import bson
from marshmallow import ValidationError, fields


class ObjectId(fields.Field):
    """A MongoDB object ID."""

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return bson.ObjectId(value)
        except (TypeError, bson.errors.InvalidId):
            raise ValidationError('Invalid ObjectId.')
