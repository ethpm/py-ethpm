import os
import json

from jsonschema import (
    validate,
    ValidationError as jsonValidationError
)
from ethpm.exceptions import (
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

        schema_data = json.load(open('./ethpm/lockfileSpecification.json'))
        package_data = json.load(open(lockfile))

        try:
            validate(package_data, schema_data)
        except jsonValidationError:
            raise ValidationError
        self.package_data = package_data

    def __repr__(self):
        name = self.name
        version = self.version
        return "<Package {0}=={1}>".format(name, version)

    @property
    def name(self):
        return self.package_data['package_name']

    @property
    def version(self):
        return self.package_data['version']
