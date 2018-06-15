import pytest

from ethpm import Package

from ethpm.exceptions import ValidationError

from ethpm.deployments import Deployments


DEPLOYMENT_DATA = {
      "SafeMathLib": {
        "contract_type": "SafeMathLib",
        "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
        "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
        "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c"
      }
    }


@pytest.fixture
def contract_factory(manifest_with_matching_deployment):
    p = Package(manifest_with_matching_deployment)
    return p.get_contract_type("SafeMathLib")


VALID_CONTRACT_TYPES = {"SafeMathLib": contract_factory}
INVALID_CONTRACT_TYPES = {"INVALID": contract_factory}


@pytest.fixture
def deployment(w3):
    return Deployments(DEPLOYMENT_DATA, VALID_CONTRACT_TYPES, w3)


@pytest.fixture
def invalid_deployment(w3):
    return Deployments(DEPLOYMENT_DATA, INVALID_CONTRACT_TYPES, w3)


def test_deployment_implements_getitem(deployment):
    assert deployment["SafeMathLib"] == DEPLOYMENT_DATA["SafeMathLib"]


@pytest.mark.parametrize("name", ("", "-abc", "A=bc", "X" * 257))
def test_deployment_getitem_with_invalid_contract_name_raises_exception(name, deployment):
    with pytest.raises(ValidationError):
        assert deployment[name]


def test_deployment_getitem_without_deployment_reference_raises_exception(deployment):
    with pytest.raises(KeyError):
        deployment["DoesNotExist"]


def test_deployment_getitem_without_contract_type_reference_raises_exception(invalid_deployment):
    with pytest.raises(ValidationError):
        invalid_deployment["SafeMathLib"]


def test_deployment_implements_get_items(deployment):
    expected_items = DEPLOYMENT_DATA.items()
    assert deployment.items() == expected_items


def test_deployment_get_items_with_invalid_contract_names_raises_exception(invalid_deployment):
    with pytest.raises(ValidationError):
        invalid_deployment.items()


def test_deployment_implements_get_values(deployment):
    expected_values = list(DEPLOYMENT_DATA.values())
    assert deployment.values() == expected_values


def test_deployment_get_values_with_invalid_contract_names_raises_exception(invalid_deployment):
    with pytest.raises(ValidationError):
        invalid_deployment.values()


def test_deployment_implements_key_lookup(deployment):
    key = "SafeMathLib" in deployment
    assert key is True


def test_deployment_implements_key_lookup_with_nonexistent_key_raises_exception(deployment):
    key = "invalid" in deployment
    assert key is False


@pytest.mark.parametrize("invalid_name", ("", "-abc", "A=bc", "X" * 257))
def test_get_contract_instance_with_invalid_name_raises_exception(deployment, invalid_name):
    with pytest.raises(ValidationError):
        deployment.get_contract_instance(invalid_name)


def test_get_contract_instance_without_reference_in_deployments_raises_exception(deployment):
    with pytest.raises(KeyError):
        deployment.get_contract_instance("InvalidContract")


def test_get_contract_instance_without_reference_in_contract_factories_raises(invalid_deployment):
    with pytest.raises(ValidationError):
        invalid_deployment.get_contract_instance("SafeMathLib")


def test_get_contract_instance_correctly_configured_raises_NotImplementedError(deployment):
    with pytest.raises(NotImplementedError):
        deployment.get_contract_instance("SafeMathLib")
