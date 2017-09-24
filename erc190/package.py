import os
import json

from jsonschema import (
    validate
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

        self.lockfile = lockfile

        schema_data = json.load(open('./erc190/schema.json'))
        package_data = json.load(open(lockfile))

        validate(package_data, schema_data)
        self.parsed_json = package_data
