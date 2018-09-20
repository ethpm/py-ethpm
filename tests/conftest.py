import copy
import json
from pathlib import Path

from eth_utils import to_canonical_address, to_hex
import pytest
from pytest_ethereum import linker as l
from web3 import Web3

from ethpm import ASSETS_DIR, V2_PACKAGES_DIR, Package
from ethpm.tools import get_manifest
from ethpm.utils.chains import create_block_uri, get_genesis_block_hash

PACKAGE_NAMES = [
    "escrow",
    "owned",
    "piper-coin",
    "safe-math-lib",
    "standard-token",
    "transferable",
    "wallet-with-send",
    "wallet",
]


def pytest_addoption(parser):
    parser.addoption("--integration", action="store_true", default=False)


def fetch_manifest(name):
    return get_manifest(name, "1.0.0.json")


MANIFESTS = {name: fetch_manifest(name) for name in PACKAGE_NAMES}


@pytest.fixture
def w3():
    w3 = Web3(Web3.EthereumTesterProvider())
    w3.eth.defaultAccount = w3.eth.accounts[0]
    return w3


@pytest.fixture
def dummy_ipfs_backend(monkeypatch):
    monkeypatch.setenv(
        "ETHPM_IPFS_BACKEND_CLASS", "ethpm.backends.ipfs.DummyIPFSBackend"
    )


@pytest.fixture
def get_manifest():
    def _get_manifest(name):
        return copy.deepcopy(MANIFESTS[name])

    return _get_manifest


@pytest.fixture(params=PACKAGE_NAMES)
def all_manifests(request, get_manifest):
    return get_manifest(request.param)


# safe-math-lib currently used as default manifest for testing
# should be extended to all_manifest_types asap
@pytest.fixture
def safe_math_manifest(get_manifest):
    return get_manifest("safe-math-lib")


@pytest.fixture
def piper_coin_manifest():
    return json.loads(
        (V2_PACKAGES_DIR / "piper-coin" / "1.0.0-pretty.json").read_text()
    )


ESCROW_DEPLOYMENT_BYTECODE = {
    "bytecode": "0x60806040526040516020806102a8833981016040525160008054600160a060020a0319908116331790915560018054600160a060020a0390931692909116919091179055610256806100526000396000f3006080604052600436106100565763ffffffff7c010000000000000000000000000000000000000000000000000000000060003504166366d003ac811461005b57806367e404ce1461008c57806369d89575146100a1575b600080fd5b34801561006757600080fd5b506100706100b8565b60408051600160a060020a039092168252519081900360200190f35b34801561009857600080fd5b506100706100c7565b3480156100ad57600080fd5b506100b66100d6565b005b600154600160a060020a031681565b600054600160a060020a031681565b600054600160a060020a031633141561019857600154604080517f9341231c000000000000000000000000000000000000000000000000000000008152600160a060020a039092166004830152303160248301525173000000000000000000000000000000000000000091639341231c916044808301926020929190829003018186803b15801561016657600080fd5b505af415801561017a573d6000803e3d6000fd5b505050506040513d602081101561019057600080fd5b506102289050565b600154600160a060020a031633141561005657600054604080517f9341231c000000000000000000000000000000000000000000000000000000008152600160a060020a039092166004830152303160248301525173000000000000000000000000000000000000000091639341231c916044808301926020929190829003018186803b15801561016657600080fd5b5600a165627a7a723058201766d3411ff91d047cf900369478c682a497a6e560cd1b2fe4d9f2d6fe13b4210029",  # noqa: E501
    "link_references": [{"offsets": [383, 577], "length": 20, "name": "SafeSendLib"}],
}


@pytest.fixture
def escrow_manifest(get_manifest):
    escrow_manifest = get_manifest("escrow")
    escrow_manifest["contract_types"]["Escrow"][
        "deployment_bytecode"
    ] = ESCROW_DEPLOYMENT_BYTECODE
    return escrow_manifest


@pytest.fixture
def get_factory(get_manifest, escrow_manifest, w3):
    def _get_factory(package, factory_name):
        manifest = get_manifest(package)
        # Special case to fetch escrow manifest with added deployment bytecode
        if package == "escrow":
            manifest = escrow_manifest
        Pkg = Package(manifest, w3)
        factory = Pkg.get_contract_factory(factory_name)
        return factory

    return _get_factory


@pytest.fixture
def invalid_manifest(safe_math_manifest):
    safe_math_manifest["manifest_version"] = 1
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
def escrow_package(solc_deployer, w3):
    escrow_manifest = ASSETS_DIR / "escrow" / "1.0.3.json"
    deployer = solc_deployer(escrow_manifest)
    escrow_strategy = l.linker(
        l.deploy("SafeSendLib"),
        l.link("Escrow", "SafeSendLib"),
        l.deploy("Escrow", w3.eth.accounts[0]),
    )
    deployer.register_strategy("Escrow", escrow_strategy)
    return deployer.deploy("Escrow")


@pytest.fixture
def safe_math_lib_package(solc_deployer, w3):
    safe_math_lib_manifest = ASSETS_DIR / "safe-math-lib" / "1.0.1.json"
    deployer = solc_deployer(safe_math_lib_manifest)
    return deployer.deploy("SafeMathLib")


@pytest.fixture
def manifest_with_no_matching_deployments(w3, tmpdir, safe_math_manifest):
    w3.testing.mine(5)
    incorrect_genesis_hash = b"\x00" * 31 + b"\x01"
    block = w3.eth.getBlock("earliest")
    block_uri = create_block_uri(w3.toHex(incorrect_genesis_hash), w3.toHex(block.hash))
    manifest = copy.deepcopy(safe_math_manifest)
    manifest["deployments"][block_uri] = {
        "SafeMathLib": {
            "contract_type": "SafeMathLib",
            "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
            "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
            "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c",
        }
    }
    return manifest


@pytest.fixture
def manifest_with_multiple_matches(w3, tmpdir, safe_math_manifest):
    w3.testing.mine(5)
    genesis_hash = get_genesis_block_hash(w3)
    block = w3.eth.getBlock("latest")
    block_uri = create_block_uri(w3.toHex(genesis_hash), w3.toHex(block.hash))
    w3.testing.mine(1)
    second_block = w3.eth.getBlock("latest")
    second_block_uri = create_block_uri(
        w3.toHex(genesis_hash), w3.toHex(second_block.hash)
    )
    manifest = copy.deepcopy(safe_math_manifest)
    manifest["deployments"][block_uri] = {
        "SafeMathLib": {
            "contract_type": "SafeMathLib",
            "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
            "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
            "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c",
        }
    }
    manifest["deployments"][second_block_uri] = {
        "SafeMathLib": {
            "contract_type": "SafeMathLib",
            "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
            "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
            "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c",
        }
    }
    return manifest


@pytest.fixture
def manifest_with_conflicting_deployments(tmpdir, safe_math_manifest):
    # two different blockchain uri's representing the same chain
    manifest = copy.deepcopy(safe_math_manifest)
    manifest["deployments"][
        "blockchain://41941023680923e0fe4d74a34bdac8141f2540e3ae90623718e47d66d1ca4a2d/block/1e96de11320c83cca02e8b9caf3e489497e8e432befe5379f2f08599f8aecede"
    ] = {
        "WrongNameLib": {
            "contract_type": "WrongNameLib",
            "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
            "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
            "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c",
        }
    }
    return manifest
