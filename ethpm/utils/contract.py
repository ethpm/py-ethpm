import re

from typing import Dict, Generator

from ethpm.exceptions import ValidationError

from web3 import Web3

from eth_utils import (
    to_bytes,
    to_dict,
    encode_hex
)


def validate_minimal_contract_data_present(contract_data: Dict):
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


def validate_contract_name(name: str):
    if not CONTRACT_NAME_REGEX.match(name):
        raise ValidationError("Contract name: {0} is not valid.".format(name))


def validate_w3_instance(w3: Web3):
    if w3 is None or not isinstance(w3, Web3):
        raise ValueError("Package does not have valid web3 instance.")


@to_dict
def generate_contract_factory_kwargs(contract_data: Dict) -> Generator:
    """
    Build a dictionary of kwargs to be passed into contract factory.
    """
    if "abi" in contract_data:
        yield "abi", contract_data["abi"]
    if "bytecode" in contract_data:
        bytecode = to_bytes(text=contract_data["bytecode"])
        yield "bytecode", encode_hex(bytecode)
    if "runtime_bytecode" in contract_data:
        runtime_bytecode = to_bytes(text=contract_data["bytecode"])
        yield "bytecode_runtime", encode_hex(runtime_bytecode)
