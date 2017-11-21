import os
import json

from jsonschema import (
    validate,
    ValidationError as jsonValidationError
)
from erc190.exceptions import (
    ValidationError
)


class Package(object):
    def __init__(self, lockfile):
        """
        A lockfile can be:

        - filesystem path
        - parsed lockfile JSON
        - lockfile URI
        """
        if not os.path.exists(lockfile):
            raise ValidationError

        self.package_identifier = lockfile

        schema_data = json.load(open('./erc190/lockfileSpecification.json'))
        package_data = json.load(open(lockfile))

        try:
            validate(package_data, schema_data)
        except jsonValidationError:
            raise ValidationError
        self.package_data = package_data
