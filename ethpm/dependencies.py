from typing import Dict, List


class Dependencies:
    """
    Access build dependencies belonging to a package.
    """

    def __init__(self, build_dependencies: Dict[str, "Package"]) -> None:
        self.build_dependencies = build_dependencies

    def __getitem__(self, key: str) -> "Package":
        return self.get(key)

    def __contains__(self, key: str) -> bool:
        return key in self.build_dependencies

    def _validate_name(self, name: str) -> None:
        if name not in self.build_dependencies:
            raise KeyError(
                "Package name: {0} not found in build dependencies.".format(name)
            )

    def get(self, key: str) -> "Package":
        self._validate_name(key)
        return self.build_dependencies.get(key)

    def items(self) -> Dict[str, "Package"]:
        item_dict = {name: self.get(name) for name in self.build_dependencies}
        return item_dict

    def values(self) -> List["Package"]:
        values = [self.get(name) for name in self.build_dependencies]
        return values

    def get_dependency_package(self, package_name: str) -> "Package":
        """
        Return a the dependency Package of the given package name.
        """
        self._validate_name(package_name)
        return self.get(package_name)
