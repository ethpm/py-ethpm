import requests

from typing import (
    Any,
    Dict,
)

from urllib import parse


INFURA_IPFS_URI_PREFIX = "https://ipfs.infura.io/ipfs/"


def fetch_ipfs_package(hash: str) -> Dict[str, Any]:
    package_uri = INFURA_IPFS_URI_PREFIX + hash
    response = requests.get(package_uri)
    response.raise_for_status()
    return response.json()


def extract_ipfs_path_from_uri(value: str) -> str:
    parse_result = parse.urlparse(value)

    if parse_result.netloc:
        if parse_result.path:
            return ''.join((parse_result.netloc, parse_result.path))
        else:
            return parse_result.netloc
    else:
        return parse_result.path.lstrip('/')


def is_ipfs_uri(value: str) -> bool:
    parse_result = parse.urlparse(value)
    if parse_result.scheme != 'ipfs':
        return False
    if not parse_result.netloc and not parse_result.path:
        return False

    return True
