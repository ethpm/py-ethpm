from typing import List

from web3 import Web3

from ethpm.exceptions import ValidationError
from ethpm.utils.chains import check_if_chain_matches_chain_uri


def validate_single_matching_uri(all_blockchain_uris: List[str], w3: Web3) -> str:
    """
    Return a single block URI after validating that it is the *only* URI in
    all_blockchain_uris that matches the w3 instance.
    """
    matching_uris = [
        uri for uri in all_blockchain_uris if check_if_chain_matches_chain_uri(w3, uri)
    ]

    if not matching_uris:
        raise ValidationError("Package has no matching URIs on chain.")
    elif len(matching_uris) != 1:
        raise ValidationError(
            "Package has too many ({0}) matching URIs: {1}.".format(
                len(matching_uris), matching_uris
            )
        )
    return matching_uris[0]
