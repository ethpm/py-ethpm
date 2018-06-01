import pytest

from ethpm.utils.ipfs import (
    extract_ipfs_path_from_uri,
    is_ipfs_uri,
)


@pytest.mark.parametrize(
    'value,expected',
    (
        (
            'ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u',
        ),
        (
            'ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u',
        ),
        (
            'ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u',
        ),
        (
            'ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/',
        ),
        (
            'ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/',
        ),
        (
            'ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/',
        ),
        (
            'ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme',
        ),
        (
            'ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme',
        ),
        (
            'ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme',
        ),
        (
            'ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/',
        ),
        (
            'ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/',
        ),
        (
            'ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/',
            'QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/',
        ),
    )
)
def test_extract_ipfs_path_from_uri(value, expected):
    actual = extract_ipfs_path_from_uri(value)
    assert actual == expected


@pytest.mark.parametrize(
    'value,expected',
    (
        ('ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', True),
        ('ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', True),
        ('ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u', True),
        ('ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/', True),
        ('ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/', True),
        ('ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/', True),
        ('ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', True),
        ('ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', True),
        ('ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', True),
        ('ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', True),
        ('ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', True),
        ('ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', True),
        # malformed
        ('ipfs//QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        ('ipfs/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        ('ipfsQmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/', False),
        # HTTP
        ('http://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', False),
        ('https://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme', False),
        # No hash
        ('ipfs://', False),
    )
)
def test_is_ipfs_uri(value, expected):
    actual = is_ipfs_uri(value)
    assert actual is expected
