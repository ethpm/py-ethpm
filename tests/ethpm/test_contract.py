from eth_utils import to_canonical_address
import pytest
from web3.contract import Contract

from ethpm import Package
from ethpm.contract import LinkableContract, validate_empty_bytes
from ethpm.exceptions import BytecodeLinkingError

ESCROW_DEPLOYMENT_BYTECODE = {
    "bytecode": "0x60806040526040516020806102a8833981016040525160008054600160a060020a0319908116331790915560018054600160a060020a0390931692909116919091179055610256806100526000396000f3006080604052600436106100565763ffffffff7c010000000000000000000000000000000000000000000000000000000060003504166366d003ac811461005b57806367e404ce1461008c57806369d89575146100a1575b600080fd5b34801561006757600080fd5b506100706100b8565b60408051600160a060020a039092168252519081900360200190f35b34801561009857600080fd5b506100706100c7565b3480156100ad57600080fd5b506100b66100d6565b005b600154600160a060020a031681565b600054600160a060020a031681565b600054600160a060020a031633141561019857600154604080517f9341231c000000000000000000000000000000000000000000000000000000008152600160a060020a039092166004830152303160248301525173000000000000000000000000000000000000000091639341231c916044808301926020929190829003018186803b15801561016657600080fd5b505af415801561017a573d6000803e3d6000fd5b505050506040513d602081101561019057600080fd5b506102289050565b600154600160a060020a031633141561005657600054604080517f9341231c000000000000000000000000000000000000000000000000000000008152600160a060020a039092166004830152303160248301525173000000000000000000000000000000000000000091639341231c916044808301926020929190829003018186803b15801561016657600080fd5b5600a165627a7a723058201766d3411ff91d047cf900369478c682a497a6e560cd1b2fe4d9f2d6fe13b4210029",  # noqa: E501
    "link_references": [{"offsets": [383, 577], "length": 20, "name": "SafeSendLib"}],
}


@pytest.fixture
def get_factory(get_manifest, w3):
    def _get_factory(package, factory_name):
        manifest = get_manifest(package)
        # Special case to add deployment bytecode to escrow manifest
        if package == "escrow":
            manifest["contract_types"]["Escrow"][
                "deployment_bytecode"
            ] = ESCROW_DEPLOYMENT_BYTECODE
        Pkg = Package(manifest, w3)
        factory = Pkg.get_contract_factory(factory_name)
        return factory

    return _get_factory


@pytest.mark.parametrize(
    "package,factory,attr_dict",
    (
        (
            "escrow",
            "Escrow",
            {"SafeSendLib": "0x4F5B11c860b37b68DE6D14Fb7e7b5f18A9A1bdC0"},
        ),
        (
            "wallet",
            "Wallet",
            {"SafeMathLib": "0xa66A05D6AB5c1c955F4D2c3FCC166AE6300b452B"},
        ),
    ),
)
def test_linkable_contract_class_handles_link_refs(
    package, factory, attr_dict, get_factory, w3
):
    factory = get_factory(package, factory)
    assert issubclass(LinkableContract, Contract)
    assert issubclass(factory, LinkableContract)
    assert factory.has_linkable_bytecode() is True
    assert factory.is_bytecode_linked is False
    factory.link_bytecode(attr_dict)
    assert factory.is_bytecode_linked is True
    offset = factory.deployment_link_refs[0]["offsets"][0]
    # Ignore lint error b/c black conflict
    link_address = to_canonical_address(list(attr_dict.values())[0])
    assert factory.bytecode[offset : offset + 20] == link_address  # noqa: E203


def test_linkable_contract_class_handles_missing_link_refs(get_manifest, w3):
    safe_math_manifest = get_manifest("safe-math-lib")
    SafeMathLib = Package(safe_math_manifest, w3)
    safe_math_lib = SafeMathLib.get_contract_factory("SafeMathLib")
    assert safe_math_lib.has_linkable_bytecode() is False
    assert safe_math_lib.is_bytecode_linked is False
    with pytest.raises(BytecodeLinkingError):
        safe_math_lib.link_bytecode(
            {"SafeMathLib": "0xa66A05D6AB5c1c955F4D2c3FCC166AE6300b452B"}
        )
    assert safe_math_lib.is_bytecode_linked is False


@pytest.mark.parametrize(
    "attr_dict",
    (
        {},
        # invalid address
        {"SafeSendLib": "abc"},
        {"SafeSendLib": 123},
        {"SafeSendLib": b"abc"},
        # Non-matching refs
        {"safe-send-lib": "0x4F5B11c860b37b68DE6D14Fb7e7b5f18A9A1bdC0"},
        {
            "SafeSendLib": "0x4F5B11c860b37b68DE6D14Fb7e7b5f18A9A1bdC0",
            "Wallet": "0xa66A05D6AB5c1c955F4D2c3FCC166AE6300b452B",
        },
    ),
)
def test_contract_factory_invalidates_incorrect_attr_dicts(get_factory, attr_dict):
    safe_send = get_factory("escrow", "SafeSendLib")
    with pytest.raises(BytecodeLinkingError):
        safe_send.link_bytecode(attr_dict)
    assert safe_send.is_bytecode_linked is False


@pytest.mark.parametrize(
    "offset,length,bytecode",
    (
        (0, 3, b"\00\00\00"),
        (1, 20, b"\01" + b"\00" * 20 + b"\01"),
        (26, 20, b"\01" + b"\00" * 20 + b"\01" * 5 + b"\00" * 20 + b"\01"),
    ),
)
def test_validate_empty_bytes(offset, length, bytecode):
    result = validate_empty_bytes(offset, length, bytecode)
    assert result is None


@pytest.mark.parametrize(
    "offset,length,bytecode",
    (
        (0, 2, b"\00"),
        (0, 3, b"\01\01\01"),
        (1, 1, b"\00\01\00\01"),
        (1, 20, b"\00" * 20 + b"\01"),
    ),
)
def test_validate_empty_bytes_invalidates(offset, length, bytecode):
    with pytest.raises(BytecodeLinkingError):
        validate_empty_bytes(offset, length, bytecode)
