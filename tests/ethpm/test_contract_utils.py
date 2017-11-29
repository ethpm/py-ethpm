import pytest

from web3 import Web3
from eth_tester import EthereumTester
from ethpm.exceptions import ValidationError
from web3.providers.eth_tester import EthereumTesterProvider

from ethpm.utils.contract import (
  validate_minimal_contract_data_present,
  validate_contract_name,
  generate_contract_factory_kwargs,
  validate_w3_instance
)


@pytest.fixture()
def w3():
    eth_tester = EthereumTester()
    w3 = Web3(EthereumTesterProvider(eth_tester))
    print("!!!")
    print(type(w3))
    return w3


@pytest.mark.parametrize(
    "contract_data",
    (
        {"abi": ""},
        {"bytecode": ""},
        {"runtime_bytecode": "", "other": ""},
        {
            "abi": "",
            "bytecode": "",
            "runtime_bytecode": ""
        }
    )
)
def test_validate_minimal_contract_data_present_validates(contract_data):
    assert validate_minimal_contract_data_present(contract_data) is None


@pytest.mark.parametrize("contract_data", ({"not_abi": ""},))
def test_validate_minimal_contract_data_present_invalidates(contract_data):
    with pytest.raises(ValidationError):
        validate_minimal_contract_data_present(contract_data)


@pytest.mark.parametrize("name", ("A1", "A-1", "A_1", "X"*256))
def test_validate_contract_name_validates(name):
    assert validate_contract_name(name) is None


@pytest.mark.parametrize("name", ("", "-abc", "A=bc", "X" * 257))
def test_validate_contract_name_invalidates(name):
    with pytest.raises(ValidationError):
        assert validate_contract_name(name)


@pytest.mark.parametrize(
    "contract_data",
    (
        {"abi": ""},
        {"bytecode": ""},
        {"abi": "", "bytecode": ""},
    )
)
def test_generate_contract_factory_kwargs(contract_data):
    contract_factory = generate_contract_factory_kwargs(contract_data)
    for key in contract_data.keys():
        assert key in contract_factory


def test_validate_w3_instance_validates(w3):
    assert validate_w3_instance(w3) is None


@pytest.mark.parametrize("w3", ("NotWeb3", b"NotWeb3", 1234))
def test_validate_w3_instance_invalidates(w3):
    with pytest.raises(ValidationError):
        assert validate_w3_instance(w3)
