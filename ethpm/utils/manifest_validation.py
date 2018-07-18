import json
import os
from typing import Any, Dict, List, Set

from jsonschema import ValidationError as jsonValidationError, validate

from ethpm import SPEC_DIR, V2_PACKAGES_DIR
from ethpm.exceptions import ValidationError

MANIFEST_SCHEMA_PATH = str(SPEC_DIR / "package.spec.json")


def _load_schema_data() -> Dict[str, Any]:
    with open(MANIFEST_SCHEMA_PATH) as schema:
        return json.load(schema)


def extract_contract_types_from_deployments(deployment_data: List[Any]) -> Set[str]:
    contract_types = set(
        deployment["contract_type"]
        for chain_deployments in deployment_data
        for deployment in chain_deployments.values()
    )
    return contract_types


def validate_manifest_against_schema(manifest: Dict[str, Any]) -> None:
    """
    Load and validate manifest against schema
    located at MANIFEST_SCHEMA_PATH.
    """
    schema_data = _load_schema_data()
    try:
        validate(manifest, schema_data)
    except jsonValidationError as e:
        raise ValidationError(
            "Manifest invalid for schema version {0}. "
            "Reason: {1}".format(schema_data["version"], e.message)
        )


def validate_deployments_are_present(manifest: Dict[str, Any]) -> None:
    if "deployments" not in manifest:
        raise ValidationError("Manifest doesn't have a deployments key.")

    if not manifest["deployments"]:
        raise ValidationError("Manifest's deployments key is empty.")


def validate_build_dependencies_are_present(manifest: Dict[str, Any]) -> None:
    if "build_dependencies" not in manifest:
        raise ValidationError("Manifest doesn't have any build dependencies.")

    if not manifest["build_dependencies"]:
        raise ValidationError("Manifest's build dependencies key is empty.")


def validate_manifest_deployments(manifest: Dict[str, Any]) -> None:
    """
    Validate that a manifest's deployments contracts reference existing contract_types.
    """
    if set(("contract_types", "deployments")).issubset(manifest):
        all_contract_types = list(manifest["contract_types"].keys())
        all_deployments = list(manifest["deployments"].values())
        all_deployment_names = extract_contract_types_from_deployments(all_deployments)
        missing_contract_types = set(all_deployment_names).difference(
            all_contract_types
        )
        if missing_contract_types:
            raise ValidationError(
                "Manifest missing references to contracts: {0}.".format(
                    missing_contract_types
                )
            )


def validate_manifest_exists(manifest_id: str) -> None:
    """
    Validate that manifest with manifest_id exists in V2_PACKAGES_DIR
    """
    manifest_path = str(V2_PACKAGES_DIR / manifest_id)
    if not os.path.exists(manifest_path):
        raise ValidationError(
            "Manifest not found in V2_PACKAGES_DIR with id: {0}".format(manifest_id)
        )
