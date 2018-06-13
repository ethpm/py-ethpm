import itertools
import json

from typing import (
    Any,
    Dict,
)

from jsonschema import (
    validate,
    ValidationError as jsonValidationError,
)

from ethpm import (
    SPEC_DIR,
    V2_PACKAGES,
)

from ethpm.exceptions import ValidationError


MANIFEST_SCHEMA_PATH = SPEC_DIR / 'package.spec.json'


def _load_schema_data() -> Dict[str, Any]:
    with open(str(MANIFEST_SCHEMA_PATH)) as schema:
        return json.load(schema)


def validate_package_against_schema(package_data: Dict[str, Any]) -> None:
    """
    Load and validate package json against schema
    located at RELEASE_PACKAGE_SCHEMA_PATH.
    """
    schema_data = _load_schema_data()
    try:
        validate(package_data, schema_data)
    except jsonValidationError:
        raise ValidationError(
            "Package:{0} invalid for schema:{1}".format(package_data, MANIFEST_SCHEMA_PATH)
        )


def validate_deployments_are_present(package_data: Dict[str, Any]) -> None:
    if "deployments" not in package_data:
        raise ValidationError("Package doesn't have a deployments key.")

    if not package_data["deployments"]:
        raise ValidationError("Package's deployments key is empty.")


def validate_package_deployments(package_data: Dict[str, Any]) -> None:
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


def check_for_build_dependencies(valid_package_data: Dict[str, Any]) -> None:
    """
    Catch packages that rely on other packages
    """
    if valid_package_data.get('build_dependencies'):
        raise NotImplementedError("Handling of package dependencies has not yet been implemented")


def validate_package_exists(package_id: str) -> None:
    """
    Validate that package with package_id exists in V2_PACKAGES
    """
    package_path = V2_PACKAGES / package_id
    if not package_path.exists():
        raise ValidationError("Package not found in V2_PACKAGES with id: {0}".format(package_id))
