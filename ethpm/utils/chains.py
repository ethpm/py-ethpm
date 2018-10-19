import re
from typing import Tuple
from urllib import parse

from cytoolz import curry
from eth_utils import add_0x_prefix, encode_hex, remove_0x_prefix
from web3 import Web3

from ethpm.typing import URI


def get_genesis_block_hash(web3: Web3) -> str:
    return web3.eth.getBlock(0)["hash"]


BLOCK = "block"

BIP122_URL_REGEX = (
    "^"
    "blockchain://"
    "(?P<chain_id>[a-zA-Z0-9]{64})"
    "/"
    "(?P<resource_type>block|transaction)"
    "/"
    "(?P<resource_hash>[a-zA-Z0-9]{64})"
    "$"
)


def is_BIP122_uri(value: URI) -> bool:
    return bool(re.match(BIP122_URL_REGEX, value))


def parse_BIP122_uri(blockchain_uri: URI) -> Tuple[str, str, str]:
    match = re.match(BIP122_URL_REGEX, blockchain_uri)
    if match is None:
        raise ValueError(f"Invalid URI format: '{blockchain_uri}'")
    chain_id, resource_type, resource_hash = match.groups()
    return (add_0x_prefix(chain_id), resource_type, add_0x_prefix(resource_hash))


def is_BIP122_block_uri(value: URI) -> bool:
    if not is_BIP122_uri(value):
        return False
    _, resource_type, _ = parse_BIP122_uri(value)
    return resource_type == BLOCK


@curry
def check_if_chain_matches_chain_uri(web3: Web3, blockchain_uri: URI) -> bool:
    chain_id, resource_type, resource_hash = parse_BIP122_uri(blockchain_uri)
    genesis_block = web3.eth.getBlock("earliest")

    if encode_hex(genesis_block["hash"]) != chain_id:
        return False

    if resource_type == BLOCK:
        resource = web3.eth.getBlock(resource_hash)
    else:
        raise ValueError(f"Unsupported resource type: {resource_type}")

    if encode_hex(resource["hash"]) == resource_hash:
        return True
    else:
        return False


BLOCK_OR_TRANSACTION_HASH_REGEX = "^(?:0x)?[a-zA-Z0-9]{64}$"


def is_block_or_transaction_hash(value: str) -> bool:
    return bool(re.match(BLOCK_OR_TRANSACTION_HASH_REGEX, value))


def create_BIP122_uri(
    chain_id: str, resource_type: str, resource_identifier: str
) -> URI:
    """
    See: https://github.com/bitcoin/bips/blob/master/bip-0122.mediawiki
    """
    if resource_type != BLOCK:
        raise ValueError("Invalid resource_type.  Must be one of 'block'")
    elif not is_block_or_transaction_hash(resource_identifier):
        raise ValueError(
            "Invalid resource_identifier.  Must be a hex encoded 32 byte value"
        )
    elif not is_block_or_transaction_hash(chain_id):
        raise ValueError("Invalid chain_id.  Must be a hex encoded 32 byte value")

    return parse.urlunsplit(
        [
            "blockchain",
            remove_0x_prefix(chain_id),
            f"{resource_type}/{remove_0x_prefix(resource_identifier)}",
            "",
            "",
        ]
    )


def create_block_uri(chain_id: str, block_identifier: str) -> URI:
    return create_BIP122_uri(chain_id, "block", remove_0x_prefix(block_identifier))
