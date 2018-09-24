Tools
=====

Builder
-------

The manifest Builder is a tool designed to help construct custom manifests. The builder is still under active development, and can only handle simple use-cases for now. 

To create a simple manifest
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For all manifests, the following ingredients are *required*.

.. code:: python

   build(
       {},
       package_name(str),
       version(str),
       manifest_version(str), ...,
   )
   # Or
   build(
       init_manifest(package_name: str, version: str, manifest_version: str="2")
       ...,
   )


The builder (i.e. ``build()``) expects a dict as the first argument. This dict can be empty, or populated if you want to extend an existing manifest.

.. doctest::

   >>> from ethpm.tools.builder import *

   >>> expected_manifest = {
   ...   "package_name": "owned",
   ...   "version": "1.0.0",
   ...   "manifest_version": "2"
   ... }
   >>> base_manifest = {"package_name": "owned"}
   >>> built_manifest = build(
   ...     {},
   ...     package_name("owned"),
   ...     manifest_version("2"),
   ...     version("1.0.0"),
   ... )
   >>> extended_manifest = build(
   ...     base_manifest,
   ...     manifest_version("2"),
   ...     version("1.0.0"),
   ... )
   >>> assert built_manifest == expected_manifest
   >>> assert extended_manifest == expected_manifest

With ``init_manifest()``, which populates "version" with "2" (the only supported EthPM specification version), unless provided with an alternative "version".

.. doctest::

   >>> build(
   ...     init_manifest("owned", "1.0.0"),
   ... )
   {'package_name': 'owned', 'version': '1.0.0', 'manifest_version': '2'}



To return a ``Package``
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   build(
       ...,
       as_package(w3: Web3),
   )

By default, the manifest builder returns a dict representing the manifest. To return a ``Package`` instance (instantiated with the generated manifest) from the builder, add the ``as_package()`` builder function with a valid ``web3`` instance to the end of the builder.

.. doctest::

   >>> from ethpm import Package
   >>> from web3 import Web3

   >>> w3 = Web3(Web3.EthereumTesterProvider())
   >>> built_package = build(
   ...     {},
   ...     package_name("owned"),
   ...     manifest_version("2"),
   ...     version("1.0.0"),
   ...     as_package(w3),
   ... )
   >>> assert isinstance(built_package, Package)


To validate a manifest
~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   build(
       ...,
       validate(),
   )

By default, the manifest builder does *not* perform any validation that the generated fields are correctly formatted. There are two ways to validate that the built manifest conforms to the EthPM V2 Specification. 
    - Return a Package, which automatically runs validation.
    - Add the ``validate()`` function to the end of the manifest builder.

.. doctest::

   >>> valid_manifest = build(
   ...     {},
   ...     package_name("owned"),
   ...     manifest_version("2"),
   ...     version("1.0.0"),
   ...     validate(),
   ... )
   >>> assert valid_manifest == {"package_name": "owned", "manifest_version": "2", "version": "1.0.0"}
   >>> invalid_manifest = build(
   ...     {},
   ...     package_name("_InvalidPkgName"),
   ...     manifest_version("2"),
   ...     version("1.0.0"),
   ...     validate(),
   ... )
   Traceback (most recent call last):
   ethpm.exceptions.ValidationError: Manifest invalid for schema version 2. Reason: '_InvalidPkgName' does not match '^[a-z][-a-z0-9]{0,255}$'


To write a manifest to disk
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   build(
       ...,
       write_to_disk(
           manifest_root_dir: Optional[Path],
           manifest_name: Optional[str],
           prettify: Optional[bool],
       ),
   )


Writes the active manifest to disk. Will not overwrite an existing manifest with the same name and root directory.

Defaults
- Writes manifest to current working directory (as returned by `os.getcwd()`) unless a ``Path`` is provided as manifest_root_dir.
- Writes manifest with a filename of "<version>.json" unless desired manifest name (which must end in ".json") is provided as manifest_name.
- Writes the minified manifest version to disk unless prettify is set to True

.. doctest::

   >>> from pathlib import Path
   >>> import tempfile
   >>> p = Path(tempfile.mkdtemp("temp"))
   >>> build(
   ...     {},
   ...     package_name("owned"),
   ...     manifest_version("2"),
   ...     version("1.0.0"),
   ...     write_to_disk(manifest_root_dir=p, manifest_name="manifest.json", prettify=True),
   ... )
   {'package_name': 'owned', 'manifest_version': '2', 'version': '1.0.0'}
   >>> with open(str(p / "manifest.json")) as f:
   ...     actual_manifest = f.read()
   >>> print(actual_manifest)
   {
        "manifest_version": "2",
        "package_name": "owned",
        "version": "1.0.0"
   }


To pin a manifest to IPFS
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   build(
       ...,
       pin_to_ipfs(
           backend: BaseIPFSBackend,
           prettify: Optional[bool],
       ),
   )

Pins the active manfiest to disk. Must be the concluding function in a builder set since it returns the IPFS pin data rather than returning the manifest for further processing.


To add meta fields
~~~~~~~~~~~~~~~~~~

.. code:: python

   build(
       ...,
       description(str),
       license(str),
       authors(*args: str),
       keywords(*args: str),
       links(*kwargs: str),
       ...,
   )

.. doctest::

   >>> BASE_MANIFEST = {"package_name": "owned", "manifest_version": "2", "version": "1.0.0"}
   >>> expected_manifest = {
   ...   "package_name": "owned",
   ...   "manifest_version": "2",
   ...   "version": "1.0.0",
   ...   "meta": {
   ...     "authors": ["Satoshi", "Nakamoto"],
   ...     "description": "An awesome package.",
   ...     "keywords": ["auth"],
   ...     "license": "MIT",
   ...     "links": {
   ...       "documentation": "www.readthedocs.com/...",
   ...       "repo": "www.github/...",
   ...       "website": "www.website.com",
   ...     }
   ...   }
   ... }
   >>> built_manifest = build(
   ...     BASE_MANIFEST,
   ...     authors("Satoshi", "Nakamoto"),
   ...     description("An awesome package."),
   ...     keywords("auth"),
   ...     license("MIT"),
   ...     links(documentation="www.readthedocs.com/...", repo="www.github/...", website="www.website.com"),
   ... )
   >>> assert expected_manifest == built_manifest


Compiler Output
~~~~~~~~~~~~~~~

To build a more complex manifest, it is required that you provide standard-json output from the solidity compiler.

Here is an example of how to compile the contracts and generate the standard-json output. More information can be found in the `Solidity Compiler <https://solidity.readthedocs.io/en/v0.4.24/using-the-compiler.html>`__ docs.

.. code:: sh

    solc --allow-paths <path-to-contract-directory> --standard-json < standard-json-input.json > owned_compiler_output.json

Sample standard-json-input.json

.. code:: json
    
    {
        "language": "Solidity",
        "sources": {
            "Contract.sol": {
                "urls": [<path-to-contract>]
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode.object"]
                }
            }
        }
    }
    

The ``compiler_output`` as used in the following examples is the entire value of the ``contracts`` key of the solc output, which contains compilation data for all compiled contracts.


To add a source
~~~~~~~~~~~~~~~

.. code:: python
  
   # To inline a source
   build(
       ...,
       inline_source(
           contract_name: str,
           compiler_output: Dict[str, Any],
           package_root_dir: Optional[Path]
       ),
       ...,
   )
   # To pin a source
   build(
       ...,
       pin_source(
           contract_name: str,
           compiler_output: Dict[str, Any],
           ipfs_backend: BaseIPFSBackend,
           package_root_dir: Optional[Path]
       ),
       ...,
   )

There are two ways to include a contract source in your manifest. 

Both strategies require that either . . .
    - The current working directory is set to the package root directory
      or
    - The package root directory is provided as an argument (``package_root_dir``)


To inline the source code directly in the manifest, use ``inline_source()`` or ``source_inliner()`` (to inline multiple sources from the same compiler_output), which requires the contract name and compiler output as args. 

.. note::
   
   `owned_compiler_output.json` below is expected to be the standard-json output generated by the solidity compiler as described `here <https://solidity.readthedocs.io/en/v0.4.24/using-the-compiler.html>`. The output must contain the `abi` and `bytecode` objects from compilation.

.. doctest::

   >>> import json
   >>> from ethpm import ASSETS_DIR, V2_PACKAGES_DIR
   >>> owned_dir = V2_PACKAGES_DIR / "owned" / "contracts"
   >>> owned_contract_source = owned_dir / "Owned.sol"
   >>> compiler_output = json.loads((ASSETS_DIR / "owned_compiler_output.json").read_text())['contracts']
   >>> expected_manifest = {
   ...   "package_name": "owned",
   ...   "version": "1.0.0",
   ...   "manifest_version": "2",
   ...   "sources": {
   ...     "./Owned.sol": """pragma solidity ^0.4.24;\n\ncontract Owned {\n    address"""
   ...     """ owner;\n    \n    modifier onlyOwner { require(msg.sender == owner); _; }\n\n    """
   ...     """constructor() public {\n        owner = msg.sender;\n    }\n}\n"""
   ...   }
   ... }
   >>> # With `inline_source()`
   >>> built_manifest = build(
   ...     BASE_MANIFEST,
   ...     inline_source("Owned", compiler_output, package_root_dir=owned_dir),
   ... )
   >>> assert expected_manifest == built_manifest
   >>> # With `source_inliner()` for multiple sources from the same compiler output
   >>> inliner = source_inliner(compiler_output, package_root_dir=owned_dir)
   >>> built_manifest = build(
   ...     BASE_MANIFEST,
   ...     inliner("Owned"),
   ...     # inliner("other_source"), etc...
   ... )
   >>> assert expected_manifest == built_manifest


To include the source as a content-addressed URI, ``Py-EthPM`` can pin your source via the Infura IPFS API. As well as the contract name and compiler output, this function requires that you provide the desired IPFS backend to pin the contract sources.

.. doctest::

   >>> from ethpm.backends.ipfs import get_ipfs_backend
   >>> ipfs_backend = get_ipfs_backend()
   >>> expected_manifest = {
   ...   "package_name": "owned",
   ...   "version": "1.0.0",
   ...   "manifest_version": "2",
   ...   "sources": {
   ...     "./Owned.sol": "ipfs://Qme4otpS88NV8yQi8TfTP89EsQC5bko3F5N1yhRoi6cwGV"
   ...   }
   ... }
   >>> # With `pin_source()`
   >>> built_manifest = build(
   ...     BASE_MANIFEST,
   ...     pin_source("Owned", compiler_output, ipfs_backend, package_root_dir=owned_dir),
   ... )
   >>> assert expected_manifest == built_manifest
   >>> # With `source_pinner()` for multiple sources from the same compiler output
   >>> pinner = source_pinner(compiler_output, ipfs_backend, package_root_dir=owned_dir)
   >>> built_manifest = build(
   ...     BASE_MANIFEST,
   ...     pinner("Owned"),
   ...     # pinner("other_source"), etc
   ... )
   >>> assert expected_manifest == built_manifest



To add a contract type
~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   build(
       ...,
       contract_type(
           contract_name: str,
           compiler_output: Dict[str, Any],
           alias: Optional[str],
           abi: Optional[bool],
           compiler: Optional[bool],
           contract_type: Optional[bool],
           deployment_bytecode: Optional[bool],
           natspec: Optional[bool],
           runtime_bytecode: Optional[bool]
       ),
       ...,
   )

The default behavior of the manifest builder's ``contract_type()`` function is to populate the manifest with all of the contract type data found in the ``compiler_output``.

.. doctest::

   >>> expected_manifest = {
   ...   'package_name': 'owned',
   ...   'manifest_version': '2',
   ...   'version': '1.0.0',
   ...   'contract_types': {
   ...     'Owned': {
   ...       'abi': [{'inputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'constructor'}],
   ...       'deployment_bytecode': {
   ...         'bytecode': '0x6080604052348015600f57600080fd5b50336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550603580605d6000396000f3006080604052600080fd00a165627a7a723058205b37f1a2213f25d063f356b0357d90ed9518d34e3af8feb0ac86586cdc1246d20029'
   ...       },
   ...       'natspec': {}
   ...     }
   ...   }
   ... }
   >>> built_manifest = build(
   ...     BASE_MANIFEST,
   ...     contract_type("Owned", compiler_output)
   ... )
   >>> assert expected_manifest == built_manifest


To select only certain contract type data to be included in your manifest, provide the desired fields as ``True`` keyword arguments. The following fields can be specified for inclusion in the manifest . . . 
    - ``abi``
    - ``compiler``
    - ``deployment_bytecode``
    - ``natspec``
    - ``runtime_bytecode``

.. doctest::

   >>> expected_manifest = {
   ...   'package_name': 'owned',
   ...   'manifest_version': '2',
   ...   'version': '1.0.0',
   ...   'contract_types': {
   ...     'Owned': {
   ...       'abi': [{'inputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'constructor'}],
   ...       'natspec': {}
   ...     }
   ...   }
   ... }
   >>> built_manifest = build(
   ...     BASE_MANIFEST,
   ...     contract_type("Owned", compiler_output, abi=True, natspec=True)
   ... )
   >>> assert expected_manifest == built_manifest

If you would like to alias your contract type, provide the desired alias as a kwarg. This will automatically include the original contract type in a ``contract_type`` field. Unless specific contract type fields are provided as kwargs, ``contract_type`` will stil default to including all availabe contract type data found in the compiler output.

.. doctest::

   >>> expected_manifest = {
   ...   'package_name': 'owned',
   ...   'manifest_version': '2',
   ...   'version': '1.0.0',
   ...   'contract_types': {
   ...     'OwnedAlias': {
   ...       'abi': [{'inputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'constructor'}],
   ...       'natspec': {},
   ...       'contract_type': 'Owned'
   ...     }
   ...   }
   ... }
   >>> built_manifest = build(
   ...     BASE_MANIFEST,
   ...     contract_type("Owned", compiler_output, alias="OwnedAlias", abi=True, natspec=True)
   ... )
   >>> assert expected_manifest == built_manifest


Checker
-------

The manifest Checker is a tool designed to help validate manifests according to the natural language spec (link). 

To validate a manifest
~~~~~~~~~~~~~~~~~~~~~~

.. doctest::

   >>> from ethpm.tools.checker import check_manifest

   >>> basic_manifest = {"package_name": "example", "version": "1.0.0", "manifest_version": "2"}
   >>> check_manifest(basic_manifest)
   {'meta': "Manifest missing a suggested 'meta' field.", 'sources': 'Manifest is missing a sources field, which defines a source tree that should comprise the full source tree necessary to recompile the contracts contained in this release.', 'contract_types': "Manifest does not contain any 'contract_types'. Packages should only include contract types that can be found in the source files for this package. Packages should not include contract types from dependencies. Packages should not include abstract contracts in the contract types section of a release."}
