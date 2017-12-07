import pytest

from ethpm.utils.chains import (
    is_BIP122_block_uri,
    parse_BIP122_uri,
)


HASH_A = '0x1234567890123456789012345678901234567890123456789012345678901234'
HASH_A_NO_PREFIX = '1234567890123456789012345678901234567890123456789012345678901234'
HASH_B = '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
HASH_B_NO_PREFIX = '1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
BLOCK_URI = 'blockchain://{0}/block/{1}'.format(HASH_A_NO_PREFIX, HASH_B_NO_PREFIX)
TRANSACTION_URI = 'blockchain://{0}/transaction/{1}'.format(HASH_A_NO_PREFIX, HASH_B_NO_PREFIX)


@pytest.mark.parametrize(
    'value,expected',
    (
        (BLOCK_URI, True),
        (TRANSACTION_URI, False),
        ('blockchain://{0}/block/{1}'.format(HASH_A, HASH_B_NO_PREFIX), False),
        ('blockchain://{0}/block/{1}'.format(HASH_A_NO_PREFIX, HASH_B), False),
        ('blockchain://{0}/block/{1}'.format(HASH_A, HASH_B_NO_PREFIX), False),
        ('blockchain://{0}/block/{1}'.format(HASH_A_NO_PREFIX[:-1], HASH_B_NO_PREFIX), False),
        ('blockchain://{0}/block/{1}'.format(HASH_A_NO_PREFIX, HASH_B_NO_PREFIX[:-1]), False),
    ),
)
def test_is_BIP122_block_uri(value, expected):
    actual = is_BIP122_block_uri(value)
    assert actual is expected


@pytest.mark.parametrize(
    'value, expected_resource_type',
    (
        (TRANSACTION_URI, 'transaction'),
        (BLOCK_URI, 'block'),
    ),
)
def test_parse_BIP122_uri(value, expected_resource_type):
    chain_id, resource_type, resource_identifier = parse_BIP122_uri(value)
    assert chain_id == HASH_A
    assert resource_type == expected_resource_type
    assert resource_identifier == HASH_B
