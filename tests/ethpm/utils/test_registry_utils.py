import pytest

from ethpm.exceptions import UriNotSupportedError

from ethpm.utils.registry import (
    is_registry_uri,
)


@pytest.mark.parametrize(
    'uri,expected',
    (
        ('ercXXX://packages.zeppelinos.eth/erc20/1.0.0', True),
        ('ercXXX://packages.zeppelinos.eth/erc20/1.0.0/', True),
        ('ercXXX://zeppelinos.eth/erc20/1.0.0', True),
        ('ercXXX://zeppelinos.eth/erc20/1.0.0/', True),
        ('ercXXX://d3cda913deb6f67967b99d67acdfa1712c293601/erc20/1.0.0', True),
        ('ercXXX://d3cda913deb6f67967b99d67acdfa1712c293601/erc20/1.0.0/', True),
        ('ercXXX://0xd3cda913deb6f67967b99d67acdfa1712c293601/erc20/1.0.0', True),
        ('ercXXX://0xd3cda913deb6f67967b99d67acdfa1712c293601/erc20/1.0.0/', True),
    )
)
def test_is_registry_uri_validates(uri, expected):
    assert is_registry_uri(uri) is expected


@pytest.mark.parametrize(
    'uri',
    (
        # invalid authority
        ('ercXXX://packages.zeppelinos.com/erc20/1.0.0'),
        ('ercXXX://package.manager.zeppelinos.eth/erc20/1.0.0'),
        ('ercXXX://packageszeppelinoseth/erc20/1.0.0'),
        ('ercXXX://0x12345/erc20/1.0.0'),
        # invalid package name
        ('ercXXX://packages.zeppelinos.eth//'),
        ('ercXXX://packages.zeppelinos.eth///'),
        ('ercXXX://packages.zeppelinos.eth//1.0.0'),
        ('ercXXX://packages.zeppelinos.eth/!rc20/1.0.0'),
        # invalid versions
        ('ercXXX://packages.zeppelinos.eth/erc20/'),
        ('ercXXX://packages.zeppelinos.eth/erc20//'),
        ('ercXXX://packages.zeppelinos.eth/erc20/v1.0.0'),
        ('ercXXX://packages.zeppelinos.eth/erc20/v1.0.0/'),
        ('ercXXX://packages.zeppelinos.eth/erc20/version_one/'),
        # malformed
        ('ercXXX:packages.zeppelinos.eth/erc20/1.0.0'),
        ('ercXXX:packages.zeppelinos.eth/erc20/1.0.0/'),
        ('ercXXX:/packages.zeppelinos.eth/erc20/1.0.0'),
        ('ercXXX:/packages.zeppelinos.eth/erc20/1.0.0/'),
        ('ercXXX/packages.zeppelinos.eth/erc20/1.0.0'),
        ('ercXXX//packages.zeppelinos.eth/erc20/1.0.0'),
        ('ercXXXpackages.zeppelinos.eth/erc20/1.0.0'),
        # wrong scheme
        ('http://packages.zeppelinos.eth/erc20/1.0.0'),
        ('ercXX://packages.zeppelinos.eth/erc20/1.0.0'),
        # no path
        ('ercXXX://'),
        # weird values
        (b'ercXXX://zeppelinos.eth/erc20/1.0.0'),
        ('1234'),
        ({}),
    )
)
def test_is_registry_uri_raises_exception_for_invalid_uris(uri):
    with pytest.raises(UriNotSupportedError):
        is_registry_uri(uri)
