import pytest

from ethpm.exceptions import ValidationError
from ethpm.manifest import validate_meta_object


@pytest.mark.parametrize(
    "meta,extra_fields",
    (
        (
            {
                "license": "MIT",
                "authors": ["author@gmail.com"],
                "description": "A Package that does things.",
                "keywords": ["ethpm", "package"],
                "links": {"documentation": "ipfs://Qm..."},
            },
            False,
        ),
        (
            {
                "license": "MIT",
                "authors": ["author@gmail.com"],
                "description": "A Package that does things.",
                "keywords": ["ethpm", "package"],
                "links": {"documentation": "ipfs://Qm..."},
                "x-hash": "0x...",
            },
            True,
        ),
    ),
)
def test_validate_meta_object_validates(meta, extra_fields):
    result = validate_meta_object(meta, allow_extra_meta_fields=extra_fields)
    assert result is None


@pytest.mark.parametrize(
    "meta,extra_fields",
    (
        # With allow_extra_meta_fields=False
        ({"invalid": "field"}, False),
        ({"license": 123}, False),
        ({"license": "MIT", "authors": "auther@gmail.com"}, False),
        (
            {
                "license": "MIT",
                "authors": ["author@gmail.com"],
                "description": ["description", "of", "package"],
            },
            False,
        ),
        (
            {
                "license": "MIT",
                "authors": ["author@gmail.com"],
                "description": "description",
                "keywords": "singlekw",
            },
            False,
        ),
        (
            {
                "license": "MIT",
                "authors": ["author@gmail.com"],
                "description": "description",
                "keywords": ["auth", "package"],
                "links": ["ipfs://Qm"],
            },
            False,
        ),
        (
            {
                "license": "MIT",
                "authors": ["author@gmail.com"],
                "description": "description",
                "keywords": ["auth", "package"],
                "links": {"documentation": "ipfs://Qm"},
                "extra": "field",
            },
            False,
        ),
        (
            {
                "license": "MIT",
                "authors": ["author@gmail.com"],
                "description": "description",
                "keywords": ["auth", "package"],
                "links": {"documentation": "ipfs://Qm"},
                "x-hash": "0x",
            },
            False,
        ),
        # With allow_extra_meta_fields=True
        # Improperly formatted "x" field
        ({"license": "MIT", "extra": "field"}, True),
    ),
)
def test_validate_meta_object_invalidates(meta, extra_fields):
    with pytest.raises(ValidationError):
        validate_meta_object(meta, allow_extra_meta_fields=extra_fields)
