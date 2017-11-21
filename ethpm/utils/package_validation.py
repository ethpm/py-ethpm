import itertools
import json
import os

from jsonschema import (
    validate,
    ValidationError as jsonValidationError
)

from ethpm import ASSETS_DIR

from ethpm.exceptions import ValidationError


RELEASE_LOCKFILE_SCHEMA_PATH = os.path.join(ASSETS_DIR, 'release-lockfile.schema.v1.json')


def load_package_data(package_id):
    """
    Load package json located in ASSETS_DIR.
    """
    with open(os.path.join(ASSETS_DIR, package_id)) as package:
        return json.load(package)


def _load_schema_data():
    with open(RELEASE_LOCKFILE_SCHEMA_PATH) as schema:
        return json.load(schema)


def validate_package_against_schema(package_data):
    """
    Load and validate package json against schema
    located at RELEASE_LOCKFILE_SCHEMA_PATH.
    """
    schema_data = _load_schema_data()
    try:
        validate(package_data, schema_data)
    except jsonValidationError:
        raise ValidationError(
            "Package:{0} invalid for schema:{1}".format(package_data, RELEASE_LOCKFILE_SCHEMA_PATH)
        )


def validate_deployments_are_present(package_data):
    if "deployments" not in package_data:
        raise ValidationError("Package doesn't have a deployments key.")

    if not package_data["deployments"]:
        raise ValidationError("Package's deployments key is empty.")


def validate_package_deployments(package_data):
    """
    Validate that a package's deployments contracts reference existing contract_types.
    """
    if set(("contract_types", "deployments")).issubset(package_data):
        all_contract_types = list(package_data["contract_types"].keys())

        all_deployments = list(package_data["deployments"].values())
        all_deployment_names = set(itertools.chain.from_iterable(
            deployment
            for deployment
            in all_deployments
        ))

        missing_contract_types = set(all_deployment_names).difference(all_contract_types)
        if missing_contract_types:
            raise ValidationError(
                    "Package missing references to contracts: {0}.".format(missing_contract_types)
            )


def check_for_build_dependencies(valid_package_data):
    """
    Catch packages that rely on other packages
    """
    if valid_package_data.get('build_dependencies'):
        raise NotImplementedError("Handling of package dependencies has not yet been implemented")


def validate_package_exists(package_id):
    """
    Validate that package with package_id exists in ASSSETS_DIR
    """
    package_path = os.path.join(ASSETS_DIR, package_id)
    if not os.path.exists(package_path):
        raise ValidationError("Package not found in ASSETS_DIR with id: {0}".format(package_id))
