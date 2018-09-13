from eth_utils import to_canonical_address
import pytest
from web3.contract import Contract

from ethpm import Package
from ethpm.contract import LinkableContract, apply_all_link_references
from ethpm.exceptions import BytecodeLinkingError, ValidationError
from ethpm.validation import validate_empty_bytes


@pytest.mark.parametrize(
    "package,factory,attr_dict",
    (
        (
            "escrow",
            "Escrow",
            {
                "SafeSendLib": to_canonical_address(
                    "0x4F5B11c860b37b68DE6D14Fb7e7b5f18A9A1bdC0"
                )
            },
        ),
        (
            "wallet",
            "Wallet",
            {
                "SafeMathLib": to_canonical_address(
                    "0xa66A05D6AB5c1c955F4D2c3FCC166AE6300b452B"
                )
            },
        ),
    ),
)
def test_linkable_contract_class_handles_link_refs(
    package, factory, attr_dict, get_factory, w3
):
    factory = get_factory(package, factory)
    linked_factory = factory.link_bytecode(attr_dict)
    assert issubclass(LinkableContract, Contract)
    assert issubclass(factory, LinkableContract)
    assert issubclass(linked_factory, LinkableContract)
    assert factory.has_linkable_bytecode() is True
    assert factory.is_bytecode_linked is False
    assert linked_factory.is_bytecode_linked is True
    # Can't link a factory that's already linked
    with pytest.raises(BytecodeLinkingError):
        linked_factory.link_bytecode(attr_dict)
    offset = factory.deployment_link_refs[0]["offsets"][0]
    link_address = to_canonical_address(list(attr_dict.values())[0])
    # Ignore lint error b/c black conflict
    assert factory.bytecode[offset : offset + 20] == b"\00" * 20  # noqa: E203
    assert linked_factory.bytecode[offset : offset + 20] == link_address  # noqa: E203


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


SAFE_SEND_ADDRESS = "0x4F5B11c860b37b68DE6D14Fb7e7b5f18A9A1bdC0"
SAFE_MATH_ADDRESS = "0xa66A05D6AB5c1c955F4D2c3FCC166AE6300b452B"
SAFE_SEND_CANON = to_canonical_address(SAFE_SEND_ADDRESS)
SAFE_MATH_CANON = to_canonical_address(SAFE_MATH_ADDRESS)


@pytest.mark.parametrize(
    "bytecode,link_refs,attr_dict,expected",
    (
        (
            bytearray(60),
            [{"length": 20, "name": "SafeSendLib", "offsets": [1]}],
            {"SafeSendLib": SAFE_SEND_CANON},
            b"\00" + SAFE_SEND_CANON + bytearray(39),
        ),
        (
            bytearray(60),
            [{"length": 20, "name": "SafeSendLib", "offsets": [1, 31]}],
            {"SafeSendLib": SAFE_SEND_CANON},
            b"\00" + SAFE_SEND_CANON + bytearray(10) + SAFE_SEND_CANON + bytearray(9),
        ),
        (
            bytearray(80),
            [
                {"length": 20, "name": "SafeSendLib", "offsets": [1, 50]},
                {"length": 20, "name": "SafeMathLib", "offsets": [25]},
            ],
            {"SafeSendLib": SAFE_SEND_CANON, "SafeMathLib": SAFE_MATH_CANON},
            b"\00"
            + SAFE_SEND_CANON
            + bytearray(4)
            + SAFE_MATH_CANON
            + bytearray(5)
            + SAFE_SEND_CANON
            + bytearray(10),
        ),
    ),
)
def test_apply_all_link_references(bytecode, link_refs, attr_dict, expected):
    actual = apply_all_link_references(bytecode, link_refs, attr_dict)
    assert actual == expected


@pytest.mark.parametrize(
    "bytecode,link_refs,attr_dict",
    (
        # Non-empty bytecode
        (
            b"\01" * 60,
            [{"length": 20, "name": "SafeSendLib", "offsets": [1]}],
            {"SafeSendLib": SAFE_SEND_CANON},
        ),
        # Illegal offset
        (
            bytearray(60),
            [{"length": 20, "name": "SafeSendLib", "offsets": [61]}],
            {"SafeSendLib": SAFE_SEND_CANON},
        ),
        # Illegal offsets
        (
            bytearray(60),
            [{"length": 20, "name": "SafeSendLib", "offsets": [1, 3]}],
            {"SafeSendLib": SAFE_SEND_CANON},
        ),
        # Illegal length
        (
            bytearray(60),
            [{"length": 61, "name": "SafeSendLib", "offsets": [0]}],
            {"SafeSendLib": SAFE_SEND_CANON},
        ),
        # Conflicting link refs
        (
            bytearray(60),
            [
                {"length": 20, "name": "SafeSendLib", "offsets": [1]},
                {"length": 20, "name": "SafeMathLib", "offsets": [15]},
            ],
            {"SafeSendLib": SAFE_SEND_CANON, "SafeMathLib": SAFE_MATH_CANON},
        ),
    ),
)
def test_apply_all_link_references_with_incorrect_args(bytecode, link_refs, attr_dict):
    with pytest.raises(BytecodeLinkingError):
        apply_all_link_references(bytecode, link_refs, attr_dict)


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


def test_linked_contract_types(get_factory):
    escrow = get_factory("escrow", "Escrow")
    linked_contract_types = escrow.linked_contract_types()
    assert linked_contract_types == ["SafeSendLib"]


def test_unlinked_factory_cannot_be_deployed(get_factory):
    escrow = get_factory("escrow", "Escrow")
    assert escrow.has_linkable_bytecode()
    assert not escrow.is_bytecode_linked
    with pytest.raises(BytecodeLinkingError):
        escrow.constructor("0x4F5B11c860b37b68DE6D14Fb7e7b5f18A9A1bdC0").transact()


@pytest.mark.parametrize(
    "offset,length,bytecode",
    (
        (0, 3, b"\00\00\00"),
        (1, 20, b"\01" + bytearray(20) + b"\01"),
        (26, 20, b"\01" + bytearray(20) + b"\01" * 5 + bytearray(20) + b"\01"),
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
        (1, 20, bytearray(20) + b"\01"),
    ),
)
def test_validate_empty_bytes_invalidates(offset, length, bytecode):
    with pytest.raises(ValidationError):
        validate_empty_bytes(offset, length, bytecode)
