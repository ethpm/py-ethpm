import json
import os

from ethpm import ASSETS_DIR
from ethpm.exceptions import ValidationError

from jsonschema import (
    validate,
    ValidationError as jsonValidationError
)

RELEASE_LOCKFILE_SCHEMA_PATH = os.path.join(ASSETS_DIR, 'release-lockfile.schema.v1.json')


def _load_package_data(package_id):
    with open(os.path.join(ASSETS_DIR, package_id)) as package:
        return json.load(package)


def _load_schema_data():
    with open(RELEASE_LOCKFILE_SCHEMA_PATH) as schema:
        return json.load(schema)


def load_and_validate_package(package_id):
    """
    Load and validate package json against schema
    located at RELEASE_LOCKFILE_SCHEMA_PATH.
    """
    schema_data = _load_schema_data()
    package_data = _load_package_data(package_id)
    try:
        validate(package_data, schema_data)
    except jsonValidationError:
        raise ValidationError(
            "Package:{0} invalid for schema:{1}".format(package_id, RELEASE_LOCKFILE_SCHEMA_PATH)
        )
    return package_data


def validate_package_exists(package_id):
    """
    Validate that package with package_id exists in ASSSETS_DIR
    """
    package_path = os.path.join(ASSETS_DIR, package_id)
    if not os.path.exists(package_path):
        raise ValidationError("Package not found in ASSETS_DIR with id: {0}".format(package_id))
