from ethpm.exceptions import ValidationError

from ethpm.utils.contract import (
    validate_contract_name,
)


class Deployments:
    """
    Deployment object to access instances of
    deployed contracts belonging to a package.
    """
    def __init__(self, deployment_data, contract_factories, w3):
        self.deployment_data = deployment_data
        self.contract_factories = contract_factories
        self.w3 = w3

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        return key in self.deployment_data

    def get(self, key):
        self._validate_name_and_references(key)
        return self.deployment_data.get(key)

    def items(self):
        item_dict = {
            name: self.get(name)
            for name
            in self.deployment_data
        }
        return item_dict.items()

    def values(self):
        values = [
            self.get(name)
            for name
            in self.deployment_data
        ]
        return values

    def get_contract_instance(self, contract_name):
        """
        Fetches a contract instance belonging to deployment
        after validating contract name.
        """
        self._validate_name_and_references(contract_name)
        raise NotImplementedError("All checks passed, but get_contract_instance API not complete.")

    def _validate_name_and_references(self, name):
        validate_contract_name(name)

        if name not in self.deployment_data:
            raise KeyError("Contract name not found in deployment data")

        if name not in self.contract_factories:
            raise ValidationError("Contract name not found in contract_factories.")
