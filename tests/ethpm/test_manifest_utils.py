import pytest

from ethpm.exceptions import ValidationError
from ethpm.manifest import validate_meta_object


@pytest.mark.parametrize(
    "meta",
    (
        {
            "license": "MIT",
            "authors": ["author@gmail.com"],
            "description": "A Package that does things.",
            "keywords": ["ethpm", "package"],
            "links": {"documentation": "ipfs://Qm..."},
        },
    ),
)
def test_validate_meta_object_validates(meta):
    result = validate_meta_object(meta)
    assert result is None


@pytest.mark.parametrize(
    "meta",
    (
        {"invalid": "field"},
        {"license": 123},
        {"license": "MIT", "authors": "auther@gmail.com"},
        {
            "license": "MIT",
            "authors": ["author@gmail.com"],
            "description": ["description", "of", "package"],
        },
        {
            "license": "MIT",
            "authors": ["author@gmail.com"],
            "description": "description",
            "keywords": "singlekw",
        },
        {
            "license": "MIT",
            "authors": ["author@gmail.com"],
            "description": "description",
            "keywords": ["auth", "package"],
            "links": ["ipfs://Qm"],
        },
        {
            "license": "MIT",
            "authors": ["author@gmail.com"],
            "description": "description",
            "keywords": ["auth", "package"],
            "links": {"documentation": "ipfs://Qm"},
            "extra": "field",
        },
    ),
)
def test_validate_meta_object_invalidates(meta):
    with pytest.raises(ValidationError):
        validate_meta_object(meta)
