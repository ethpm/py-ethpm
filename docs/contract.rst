LinkableContract
================

`Py-EthPM` uses a custom subclass of ``Web3.contract.Contract`` to manage contract factories and instances which might require bytecode linking. To create a deployable contract factory, both the contract type's `abi` and `deployment_bytecode` must be available in the Package's manifest.

.. doctest::

   >>> from eth_utils import is_address, to_canonical_address
   >>> from web3 import Web3
   >>> from ethpm import Package, V2_PACKAGES_DIR

   >>> PACKAGING_EXAMPLES = V2_PACKAGES_DIR.parent.parent / 'tests' / 'ethpm' / 'packaging-examples'
   >>> w3 = Web3(Web3.EthereumTesterProvider())
   >>> escrow_manifest_path = str(PACKAGING_EXAMPLES / 'escrow' / '1.0.3.json')

   >>> # Try to deploy from unlinked factory
   >>> EscrowPackage = Package.from_file(escrow_manifest_path, w3)
   >>> EscrowFactory = EscrowPackage.get_contract_factory("Escrow")
   >>> assert EscrowFactory.needs_bytecode_linking
   >>> escrow_instance = EscrowFactory.constructor(w3.eth.accounts[0]).transact()
   Traceback (most recent call last):
        ...
   ethpm.exceptions.BytecodeLinkingError: Contract cannot be deployed until its bytecode is linked.

   >>> # Deploy SafeSendLib
   >>> SafeSendFactory = EscrowPackage.get_contract_factory("SafeSendLib")
   >>> safe_send_tx_hash = SafeSendFactory.constructor().transact()
   >>> safe_send_tx_receipt = w3.eth.waitForTransactionReceipt(safe_send_tx_hash)

   >>> # Link Escrow factory to deployed SafeSendLib instance
   >>> LinkedEscrowFactory = EscrowFactory.link_bytecode({"SafeSendLib": to_canonical_address(safe_send_tx_receipt.contractAddress)})
   >>> assert LinkedEscrowFactory.needs_bytecode_linking is False
   >>> escrow_tx_hash = LinkedEscrowFactory.constructor(w3.eth.accounts[0]).transact()
   >>> escrow_tx_receipt = w3.eth.waitForTransactionReceipt(escrow_tx_hash)
   >>> assert is_address(escrow_tx_receipt.contractAddress)


Properties
----------

.. py:attribute:: LinkableContract.deployment_link_refs

   A list of link reference data for the deployment bytecode, if present in the manifest data used to generate a ``LinkableContract`` factory. Deployment bytecode link reference data must be present in a manifest in order to generate a factory for a contract which requires bytecode linking.

.. py:attribute:: LinkableContract.runtime_link_refs

   A list of link reference data for the runtime bytecode, if present in the manifest data used to generate a ``LinkableContract`` factory. Runtime bytecode link reference data must be present in a manifest in order to use ``pytest-ethereum``'s ``Deployer`` for a contract which requires bytecode linking.

.. py:attribute:: LinkableContract.needs_bytecode_linking

   A boolean attribute used to indicate whether a contract factory has unresolved link references, which must be resolved before a new contract instance can be deployed or instantiated at a given address.


Methods
-------

.. py:classmethod:: LinkableContract.link_bytecode(attr_dict)

   This method returns a newly created contract factory with the applied link references defined in the `attr_dict`. This method expects `attr_dict` to be of the type ``Dict[`contract_name`: `address`]`` for all link references that are unlinked.

