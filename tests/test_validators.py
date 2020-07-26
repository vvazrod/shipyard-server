import unittest

from marshmallow import ValidationError

from shipyard.validators import validate_ip, validate_devices


class TestValidators(unittest.TestCase):

    def test_validate_ip(self):
        try:
            validate_ip('0.0.0.0')
        except ValidationError:
            self.fail('Correct IP address validation returned an error.')

        with self.assertRaises(ValidationError):
            validate_ip('test')

    def test_validate_devices(self):
        try:
            validate_devices(['/dev/null', '/dev/tty'])
        except ValidationError:
            self.fail('Correct device names validation returned an error.')

        with self.assertRaises(ValidationError):
            validate_devices(['fail', 'test'])
