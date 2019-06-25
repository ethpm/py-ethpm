import pytest

from ethpm.exceptions import ValidationError
from ethpm.validation.misc import validate_address


@pytest.mark.parametrize(
    "address", (b"\xd3\xcd\xa9\x13\xde\xb6\xf6yg\xb9\x9dg\xac\xdf\xa1q,)6\x01",)
)
def test_validate_address_accepts_canonicalized_addresses(address):
    result = validate_address(address)
    assert result is None


@pytest.mark.parametrize(
    "address",
    (
        "d3cda913deb6f67967b99d67acdfa1712c293601",
        "0xd3cda913deb6f67967b99d67acdfa1712c293601",
        "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
        "\xd3\xcd\xa9\x13\xde\xb6\xf6yg\xb9\x9dg\xac\xdf\xa1q,)6\x01xd",
    ),
)
def test_validate_address_rejects_incorrectly_formatted_adresses(address):
    with pytest.raises(ValidationError):
        validate_address(address)
