import re
from typing import Any, Dict, Generator, List, Tuple

from eth_utils import to_dict
from solc import compile_files
from web3 import Web3

from ethpm import V2_PACKAGES_DIR
from ethpm.exceptions import InsufficientAssetsError, ValidationError


def validate_minimal_contract_factory_data(contract_data: Dict[str, str]) -> None:
    """
    Validate that contract data in a package contains at least an "abi" and
    "deployment_bytecode" necessary to generate a deployable contract factory.
    """
    if not all(key in contract_data.keys() for key in ("abi", "deployment_bytecode")):
        raise InsufficientAssetsError(
            "Minimum required contract data to generate a deployable "
            "contract factory (abi & deployment_bytecode) not found."
        )


CONTRACT_NAME_REGEX = re.compile("^[a-zA-Z][-a-zA-Z0-9_]{0,255}$")


def validate_contract_name(name: str) -> None:
    if not CONTRACT_NAME_REGEX.match(name):
        raise ValidationError(f"Contract name: {name} is not valid.")


def validate_w3_instance(w3: Web3) -> None:
    if w3 is None or not isinstance(w3, Web3):
        raise ValueError("Package does not have valid web3 instance.")


@to_dict
def generate_contract_factory_kwargs(
    contract_data: Dict[str, Any]
) -> Generator[Tuple[str, Any], None, None]:
    """
    Build a dictionary of kwargs to be passed into contract factory.
    """
    if "abi" in contract_data:
        yield "abi", contract_data["abi"]

    if "deployment_bytecode" in contract_data:
        yield "bytecode", contract_data["deployment_bytecode"]["bytecode"]
        if "link_references" in contract_data["deployment_bytecode"]:
            yield "unlinked_references", tuple(
                contract_data["deployment_bytecode"]["link_references"]
            )

    if "runtime_bytecode" in contract_data:
        yield "bytecode_runtime", contract_data["runtime_bytecode"]["bytecode"]
        if "link_references" in contract_data["runtime_bytecode"]:
            yield "linked_references", tuple(
                contract_data["runtime_bytecode"]["link_references"]
            )


def compile_contracts(contract_name: str, alias: str, paths: List[str]) -> str:
    """
    Compile multiple contracts to bytecode.
    """
    bin_id = f"{contract_name}.sol:{contract_name}"
    contract_paths = [(V2_PACKAGES_DIR / alias / path[1:]) for path in paths]
    compiled_source = compile_files(contract_paths)
    bin_lookup = V2_PACKAGES_DIR / alias / bin_id
    compiled_source_bin = compiled_source[bin_lookup]["bin"]
    return compiled_source_bin
