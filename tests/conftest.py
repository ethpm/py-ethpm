import copy
import json
import pytest

from eth_tester import (
    EthereumTester,
    MockBackend,
)

from web3 import Web3

from web3.providers.eth_tester import EthereumTesterProvider

from ethpm.utils.chains import (
    get_chain_id,
    create_block_uri,
)


@pytest.fixture()
def w3():
    eth_tester = EthereumTester(MockBackend())
    w3 = Web3(EthereumTesterProvider(eth_tester))
    return w3


@pytest.fixture
def valid_package():
    with open("ethpm/assets/v2-packages/safe-math-lib/1.0.0.json") as file_obj:
        return json.load(file_obj)


@pytest.fixture()
def invalid_package(valid_package):
    valid_package['manifest_version'] = 1
    return valid_package


@pytest.fixture
def package_with_no_deployments(valid_package):
    package = copy.deepcopy(valid_package)
    package.pop("deployments")
    return package


@pytest.fixture
def package_with_empty_deployments(tmpdir, valid_package):
    package = copy.deepcopy(valid_package)
    package["deployments"] = {}
    return package


@pytest.fixture
def package_with_matching_deployment(w3, tmpdir, valid_package):
    w3.testing.mine(5)
    chain_id = get_chain_id(w3)
    block = w3.eth.getBlock("earliest")
    block_uri = create_block_uri(w3.toHex(chain_id), w3.toHex(block.hash))
    package = copy.deepcopy(valid_package)
    package["deployments"] =  {}
    package["deployments"][block_uri] = {
      "SafeMathLib": {
        "contract_type": "SafeMathLib",
        "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
        "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
        "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c"
      }
    }
    return package


@pytest.fixture
def package_with_no_matching_deployments(w3, tmpdir, valid_package):
    w3.testing.mine(5)
    incorrect_chain_id = (b'\x00' * 31 + b'\x01')
    block = w3.eth.getBlock("earliest")
    block_uri = create_block_uri(w3.toHex(incorrect_chain_id), w3.toHex(block.hash))
    package = copy.deepcopy(valid_package)
    package["deployments"][block_uri] = {
      "SafeMathLib": {
        "contract_type": "SafeMathLib",
        "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
        "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
        "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c"
      }
    }
    return package


@pytest.fixture
def package_with_multiple_matches(w3, tmpdir, valid_package):
    w3.testing.mine(5)
    chain_id = get_chain_id(w3)
    block = w3.eth.getBlock("latest")
    block_uri = create_block_uri(w3.toHex(chain_id), w3.toHex(block.hash))
    w3.testing.mine(1)
    second_block = w3.eth.getBlock("latest")
    second_block_uri = create_block_uri(w3.toHex(chain_id), w3.toHex(second_block.hash))
    package = copy.deepcopy(valid_package)
    package['deployments'][block_uri] = {
        "SafeMathLib": {
            "contract_type": "SafeMathLib",
            "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
            "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
            "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c"
        }
    }
    package['deployments'][second_block_uri] = {
        "SafeMathLib": {
            "contract_type": "SafeMathLib",
            "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
            "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
            "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c"
        }
    }
    return package


@pytest.fixture
def package_with_conflicting_deployments(tmpdir, valid_package):
    package = copy.deepcopy(valid_package)
    package["deployments"]["blockchain://41941023680923e0fe4d74a34bdac8141f2540e3ae90623718e47d66d1ca4a2d/block/1e96de11320c83cca02e8b9caf3e489497e8e432befe5379f2f08599f8aecede"] = {
        "WrongNameLib": {
            "contract_type": "WrongNameLib",
            "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
            "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
            "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c"
        }
    }
    return package
