import json
from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple  # ignore: F401

from eth_utils import to_dict

from ethpm.backends.ipfs import get_ipfs_backend
from ethpm.utils.filesystem import load_json_from_file_path
from ethpm.utils.ipfs import create_ipfs_uri
from ethpm.validation import validate_manifest_version, validate_package_name


class Manifest:
    """
    Class for handling manifest generation that represents a set of packaged contract(s).

    Expected directory structure:
        |-- combined.json (solc output)
        |-- ... (will write manifests to disk here) ...
        |-- contracts/
        |   |-- Contract1.sol
        |   |-- Contract2.sol
    """

    def __init__(self, manifest_version: str, package_name: str, version: str) -> None:
        validate_manifest_version(manifest_version)
        validate_package_name(package_name)
        self.manifest_version = manifest_version
        self.package_name = package_name
        self.version = version
        self.ipfs_backend = get_ipfs_backend()
        self.solc_path = None  # type: Path
        self.sources = {}  # type: Dict[str,str]
        self.contract_types = {}  # type: Dict[str,Any]

    def link_solc_output(
        self, solc_path: Path, contract_types: List[str] = None
    ) -> None:
        """
        Populate the manifest with data from a linked solc output.

        :solc_path
            Path leading to a file containing output from solc
            Solc output *must* be generated with `abi` & `devdoc` flags enabled

            i.e.
        `solc --output-dir ./ --combined-json abi,bin,devdoc,interface,userdoc contracts/Owned.sol`

        :contract_types
            List containing the contract types to be included in this manifest.

            * Packages should only include contract types that can be
              found in the source files for this package.
            * Packages should not include abstract contracts in the contract types section.
            * Packages should not include contract types from dependencies.
        """
        if self.solc_path:
            raise AttributeError(
                "This manifest has already been linked to solc output located at {0}.".format(
                    self.solc_path
                )
            )
        self.solc_path = solc_path
        solc = load_json_from_file_path(self.solc_path)
        for contract in solc["contracts"]:
            contract_path, contract_name = contract.split(":")
            source_data = self._create_source(contract_path)
            setattr(self, "sources", {**self.sources, **source_data})
            if contract_types is not None and contract_name in contract_types:
                contract_type_data = self._create_contract_type(
                    contract_name, contract, solc
                )
                setattr(
                    self,
                    "contract_types",
                    {**self.contract_types, **contract_type_data},
                )

    @to_dict
    def _create_contract_type(
        self, contract_name: str, contract: str, solc: Dict[str, Any]
    ) -> Generator[Tuple[str, Any], None, None]:
        yield contract_name, self._generate_contract_type_dict(contract, solc)

    @to_dict
    def _generate_contract_type_dict(self, contract: str, solc: Dict[str, Any]) -> Generator[Tuple[str, Any], None, None]:
        yield "abi", json.loads(solc["contracts"][contract]["abi"])
        yield "natspec", json.loads(solc["contracts"][contract]["devdoc"])

    @to_dict
    def _create_source(self, contract_path: str) -> Generator[Tuple[str, Any], None, None]:
        [ipfs_return_data] = self.ipfs_backend.pin_assets(
            Path(self.solc_path).parent / contract_path
        )
        ipfs_hash = ipfs_return_data["Hash"]
        ipfs_uri = create_ipfs_uri(ipfs_hash)
        yield "./{0}".format(contract_path), ipfs_uri

    def add_meta(self, **kwargs: Any) -> None:
        """
        Adds metadata to the `meta` key in this manifest.
        Suggested kwarg types
        - `authors`         List[str]
        - `license`         str
        - `description`     str
        - `keywords`        List[str]
        - `links`           Dict[str,str]
            Recommended keys for `links`
            - `website`
            - `documentation`
            - `repository`
        """
        self.meta = {key: value for key, value in kwargs.items() if value}

    def pretty(self) -> str:
        """
        Returns a string of a pretty printed version of this manifest.
        """
        attr_dict = self._generate_attr_dict()
        return json.dumps(attr_dict, indent=4, sort_keys=True)

    def minified(self) -> str:
        """
        Returns a string of a minified version of this manifest.
        """
        attr_dict = self._generate_attr_dict()
        return json.dumps(attr_dict, separators=(",", ":"), sort_keys=True)

    # TODO implement `write_pretty_to_disk` w/o indenting ABI
    def write_minified_to_disk(self) -> Path:
        """
        Returns a path leading to a minified version of this manifest written to disk.
        Manifest is written to the same dir in which the `contracts/` dir is located.
        """
        manifest_contents = self.minified()
        path = self.solc_path.parent / str(self.version + ".json")
        path.write_text(manifest_contents)
        return path

    @to_dict
    def _generate_attr_dict(self) -> Generator[Tuple[str, Any], Any, None]:
        for key, value in self.__dict__.items():
            if key is not "solc_path" and key is not "ipfs_backend":
                if value:
                    yield key, value
