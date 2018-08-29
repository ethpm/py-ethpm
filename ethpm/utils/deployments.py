from typing import Any, Dict, Generator, List, Tuple

from eth_utils import to_bytes, to_canonical_address, to_tuple
from web3 import Web3

from ethpm.exceptions import BytecodeLinkingError, ValidationError


def get_linked_deployments(deployments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns all deployments found in a chain URI's deployment data that contain link dependencies.
    """
    linked_deployments = {
        dep: data
        for dep, data in deployments.items()
        if "runtime_bytecode" in data
        and "link_dependencies" in data["runtime_bytecode"]
    }
    for deployment, data in linked_deployments.items():
        if deployment == data["runtime_bytecode"]["link_dependencies"][0]["value"]:
            raise BytecodeLinkingError(
                "Link dependency found in {0} deployment that references it's own contract "
                "instance, which is disallowed".format(deployment)
            )
    return linked_deployments


def validate_link_dependencies(
    link_deps: Tuple[Tuple[int, str]], bytecode: bytes
) -> None:
    """
    Validates that normalized link_dependencies (offset, expected_bytes)
    match the corresponding bytecode.
    """
    offsets, values = zip(*link_deps)
    for idx, offset in enumerate(offsets):
        value = values[idx]
        # https://github.com/python/mypy/issues/4975
        offset_value = int(offset)  # type: ignore
        dep_length = len(value)  # type: ignore
        end_of_bytes = offset_value + dep_length
        # Ignore b/c whitespace around ':' conflict b/w black & flake8
        actual_bytes = bytecode[offset_value:end_of_bytes]  # noqa: E203
        if actual_bytes != values[idx]:
            raise ValidationError(
                "Error validating link dependency. "
                "Offset: {0} "
                "Value: {1} "
                "Bytecode: {2} .".format(offset, values[idx], bytecode)
            )


@to_tuple
def normalize_link_dependencies(
    data: List[Dict[str, Any]]
) -> Generator[Tuple[int, str, str], None, None]:
    """
    Return a tuple of information representing all insertions of a link dependency.
    (offset, type, value)
    """
    for deployment in data:
        for offset in deployment["offsets"]:
            yield offset, deployment["type"], deployment["value"]


def validate_deployments_tx_receipt(deployments: Dict[str, Any], w3: Web3) -> None:
    """
    Validate that address and block hash found in deployment data match what is found on-chain.
    """
    for name, data in deployments.items():
        if "transaction" in data:
            tx_hash = data["transaction"]
            tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
            tx_address = tx_receipt["contractAddress"]

            if to_canonical_address(tx_address) != to_canonical_address(
                data["address"]
            ):
                raise ValidationError(
                    "Error validating tx_receipt for {0} deployment. "
                    "Address found in deployment: {1} "
                    "Does not match "
                    "Address found on tx_receipt: {2}.".format(
                        name, data["address"], tx_address
                    )
                )

            if "block" in data:
                if tx_receipt["blockHash"] != to_bytes(hexstr=data["block"]):
                    raise ValidationError(
                        "Error validating tx_receipt for {0} deployment. "
                        "Block found in deployment: {1} "
                        "Does not match "
                        "Block found on tx_receipt: {2}.".format(
                            name, data["block"], tx_receipt["blockHash"]
                        )
                    )
