import copy
import json
import pytest

from web3 import Web3

from web3.providers.eth_tester import EthereumTesterProvider

from ethpm import V2_PACKAGES_DIR

from ethpm.utils.chains import (
    get_chain_id,
    create_block_uri,
)


PACKAGE_NAMES = [
    'escrow',
    'owned',
    'piper-coin',
    'safe-math-lib',
    'standard-token',
    'transferable',
    'wallet-with-send',
    'wallet',
]



@pytest.fixture()
def w3():
    w3 = Web3(EthereumTesterProvider())
    w3.eth.defaultAccount = w3.eth.accounts[0]
    return w3


@pytest.fixture()
def all_manifests():
    manifests = []
    for pkg in PACKAGE_NAMES:
        with open(str(V2_PACKAGES_DIR / pkg / '1.0.0.json')) as file_obj:
            manifest = json.load(file_obj)
            manifests.append(manifest)
    return manifests


# safe-math-lib currently used as default manifest for testing
# should be extended to all_manifest_types asap
@pytest.fixture
def safe_math_manifest():
    with open(str(V2_PACKAGES_DIR / 'safe-math-lib' / '1.0.0.json')) as file_obj:
        return json.load(file_obj)


@pytest.fixture
def owned_manifest():
    with open(str(V2_PACKAGES_DIR / 'owned' / '1.0.0.json')) as file_obj:
        return json.load(file_obj)

# standalone = no `build_dependencies` which aren't fully supported yet
@pytest.fixture
def all_standalone_manifests(all_manifests):
    standalone_manifests = [mnfst for mnfst in all_manifests if "build_dependencies" not in mnfst]
    return standalone_manifests


@pytest.fixture()
def invalid_manifest(safe_math_manifest):
    safe_math_manifest['manifest_version'] = 1
    return safe_math_manifest


@pytest.fixture
def manifest_with_no_deployments(safe_math_manifest):
    manifest = copy.deepcopy(safe_math_manifest)
    manifest.pop("deployments")
    return manifest


@pytest.fixture
def manifest_with_empty_deployments(tmpdir, safe_math_manifest):
    manifest = copy.deepcopy(safe_math_manifest)
    manifest["deployments"] = {}
    return manifest


@pytest.fixture
def manifest_with_matching_deployment(w3, tmpdir, safe_math_manifest):
    w3.testing.mine(5)
    chain_id = get_chain_id(w3)
    block = w3.eth.getBlock("earliest")
    block_uri = create_block_uri(w3.toHex(chain_id), w3.toHex(block.hash))
    manifest = copy.deepcopy(safe_math_manifest)
    manifest["deployments"] =  {}
    manifest["deployments"][block_uri] = {
      "SafeMathLib": {
        "contract_type": "SafeMathLib",
        "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
        "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
        "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c"
      }
    }
    return manifest


@pytest.fixture
def manifest_with_no_matching_deployments(w3, tmpdir, safe_math_manifest):
    w3.testing.mine(5)
    incorrect_chain_id = (b'\x00' * 31 + b'\x01')
    block = w3.eth.getBlock("earliest")
    block_uri = create_block_uri(w3.toHex(incorrect_chain_id), w3.toHex(block.hash))
    manifest = copy.deepcopy(safe_math_manifest)
    manifest["deployments"][block_uri] = {
      "SafeMathLib": {
        "contract_type": "SafeMathLib",
        "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
        "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
        "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c"
      }
    }
    return manifest


@pytest.fixture
def manifest_with_multiple_matches(w3, tmpdir, safe_math_manifest):
    w3.testing.mine(5)
    chain_id = get_chain_id(w3)
    block = w3.eth.getBlock("latest")
    block_uri = create_block_uri(w3.toHex(chain_id), w3.toHex(block.hash))
    w3.testing.mine(1)
    second_block = w3.eth.getBlock("latest")
    second_block_uri = create_block_uri(w3.toHex(chain_id), w3.toHex(second_block.hash))
    manifest = copy.deepcopy(safe_math_manifest)
    manifest['deployments'][block_uri] = {
        "SafeMathLib": {
            "contract_type": "SafeMathLib",
            "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
            "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
            "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c"
        }
    }
    manifest['deployments'][second_block_uri] = {
        "SafeMathLib": {
            "contract_type": "SafeMathLib",
            "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
            "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
            "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c"
        }
    }
    return manifest


@pytest.fixture
def manifest_with_conflicting_deployments(tmpdir, safe_math_manifest):
    manifest = copy.deepcopy(safe_math_manifest)
    manifest["deployments"]["blockchain://41941023680923e0fe4d74a34bdac8141f2540e3ae90623718e47d66d1ca4a2d/block/1e96de11320c83cca02e8b9caf3e489497e8e432befe5379f2f08599f8aecede"] = {
        "WrongNameLib": {
            "contract_type": "WrongNameLib",
            "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
            "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
            "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c"
        }
    }
    return manifest
