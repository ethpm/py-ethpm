Manifest Builder
================

The Manifest Builder is a tool designed to help construct custom manifests. The builder is still under active development, and can only handle simple use-cases for now. 


Cookbook
--------

To create a simple manifest
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For all manifests, the following fields are *required*.
    - ``package_name``      (i.e. "owned")
    - ``version``           (i.e. "1.0.0")
    - ``manifest_version``  (i.e. "2")

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


To return a ``Package``
~~~~~~~~~~~~~~~~~~~~~~~

By default, the manifest builder returns a dict representing the manifest. To return a ``Package`` instance (instantiated with the generated manifest) from the builder, add the ``return_package()`` builder function with a valid ``web3`` instance to the end of the builder.

.. doctest::

   >>> from ethpm import Package
   >>> from web3 import Web3

   >>> w3 = Web3(Web3.EthereumTesterProvider())
   >>> built_package = build(
   ...     {},
   ...     package_name("owned"),
   ...     manifest_version("2"),
   ...     version("1.0.0"),
   ...     return_package(w3),
   ... )
   >>> assert isinstance(built_package, Package)



To validate the built manifest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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


To add meta fields
~~~~~~~~~~~~~~~~~~

The following functions are available to populate the "meta" field of a manifest.

    - ``description()`` accepts a single string
    - ``license()``     accepts a single string
    - ``authors()``     accepts any number of strings
    - ``keywords()``    accepts any number of strings
    - ``links()``       accepts any kind & number of keyword arguments

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

There are two ways to include a contract source in your manifest. 

Both strategies require that either . . .
    - The current working directory is set to the package root directory
      or
    - The package root directory is provided as an argument (``package_root_dir``)


To inline the source code directly in the manifest, use the ``inline_source()`` function, which requires the contract name and compiler output as args. 

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
   >>> built_manifest = build(
   ...     BASE_MANIFEST,
   ...     inline_source("Owned", compiler_output, package_root_dir=owned_dir),
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
   >>> built_manifest = build(
   ...     BASE_MANIFEST,
   ...     pin_source("Owned", compiler_output, ipfs_backend, package_root_dir=owned_dir),
   ... )
   >>> assert expected_manifest == built_manifest



To add a contract type
~~~~~~~~~~~~~~~~~~~~~~

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
