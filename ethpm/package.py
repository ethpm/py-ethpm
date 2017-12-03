from ethpm.exceptions import ValidationError

from ethpm.utils.package_validation import (
    load_package_data,
    validate_package_against_schema,
    validate_package_exists,
    validate_package_deployments,
)
from ethpm.utils.contract import (
    generate_contract_factory_kwargs,
    validate_contract_name,
    validate_minimal_contract_data_present,
    validate_w3_instance,
)


class Package(object):

    def __init__(self, package_id, w3=None):
        """
        A lockfile can be:
        - filesystem path
        - parsed lockfile JSON
        - lockfile URI
        """
        self.w3 = w3
        self.package_id = package_id

        validate_package_exists(package_id)
        package_data = load_package_data(package_id)
        validate_package_against_schema(package_data)
        validate_package_deployments(package_data)

        self.package_data = package_data

    def set_default_w3(self, w3):
        """
        Set the default Web3 instance.
        """
        self.w3 = w3

    def get_contract_type(self, name, w3=None):
        """
        API to generate a contract factory class.
        """
        current_w3 = None

        if w3 is not None:
            current_w3 = w3
        else:
            current_w3 = self.w3

        validate_contract_name(name)
        validate_w3_instance(current_w3)

        if name in self.package_data['contract_types']:
            contract_data = self.package_data['contract_types'][name]
            validate_minimal_contract_data_present(contract_data)
            contract_kwargs = generate_contract_factory_kwargs(contract_data)
            contract_factory = current_w3.eth.contract(**contract_kwargs)
            return contract_factory
        raise ValidationError("Package does not have contract by name: {}.".format(name))

    def __repr__(self):
        name = self.name
        version = self.version
        return "<Package {0}=={1}>".format(name, version)

    @property
    def name(self):
        return self.package_data['package_name']

    @property
    def version(self):
        return self.package_data['version']
