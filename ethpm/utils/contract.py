import re

from typing import (
    Any,
    Dict,
    Generator,
    List,
    Tuple,
)

from eth_utils import (
    to_bytes,
    to_dict,
    encode_hex,
)

from solc import compile_files

from web3 import Web3

from ethpm import V2_PACKAGES
from ethpm.exceptions import ValidationError


def validate_minimal_contract_data_present(contract_data: Dict[str, str]) -> None:
    """
    Validate that contract data contains at least one of the following keys
    necessary to generate contract factory.

    "abi", "bytecode", "runtime_bytecode"
    """
    if not any(key in contract_data.keys() for key in ("abi", "bytecode", "runtime_bytecode")):
        raise ValidationError(
            "Minimum required contract data (abi/bytecode/runtime_bytecode) not found."
        )


CONTRACT_NAME_REGEX = re.compile("^[a-zA-Z][-a-zA-Z0-9_]{0,255}$")


def validate_contract_name(name: str) -> None:
    if not CONTRACT_NAME_REGEX.match(name):
        raise ValidationError("Contract name: {0} is not valid.".format(name))


def validate_w3_instance(w3: Web3) -> None:
    if w3 is None or not isinstance(w3, Web3):
        raise ValueError("Package does not have valid web3 instance.")


@to_dict
def generate_contract_factory_kwargs(
        contract_data: Dict[str, Any]) -> Generator[Tuple[str, Any], None, None]:
    """
    Build a dictionary of kwargs to be passed into contract factory.
    """
    if "abi" in contract_data:
        yield "abi", contract_data["abi"]
    if "bytecode" in contract_data:
        bytecode = to_bytes(text=contract_data["bytecode"]["bytecode"])
        yield "bytecode", encode_hex(bytecode)
    if "runtime_bytecode" in contract_data:
        runtime_bytecode = to_bytes(text=contract_data["runtime_bytecode"]["bytecode"])
        yield "bytecode_runtime", encode_hex(runtime_bytecode)


def compile_contracts(contract_name: str, alias: str, paths: List[str]) -> str:
    '''
    Compile multiple contracts to bytecode.
    '''
    bin_id = '{0}.sol:{0}'.format(contract_name)
    contract_paths = [
        "{dir}/{alias}{path}".format(dir=V2_PACKAGES, alias=alias, path=path[1:])
        for path in paths
    ]
    compiled_source = compile_files(contract_paths)
    compiled_source_bin = compiled_source[
        "{dir}/{alias}/contracts/{id}".format(dir=V2_PACKAGES, alias=alias, id=bin_id)]['bin']
    return compiled_source_bin
