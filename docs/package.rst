Packages
========

The ``Package`` object will function much like the ``Contract`` class
provided by ``web3``. Rather than instantiating the base class provided
by ``ethpm``, you will instead use a ``classmethod`` which generates a
new ``Package`` class for a given package.

``Package`` objects *must* be instantiated with a valid ``web3`` object.

-  Creating a ``Package`` object from a local manifest file.

.. doctest::
  
   >>> from ethpm import Package, V2_PACKAGES_DIR
   >>> from web3 import Web3

   >>> owned_manifest_path = str(V2_PACKAGES_DIR / 'owned' / '1.0.0.json')
   >>> w3 = Web3(Web3.EthereumTesterProvider())

   >>> OwnedPackage = Package.from_file(owned_manifest_path, w3)
   >>> assert isinstance(OwnedPackage, Package)

-  Creating a ``Package`` object from a content-addressed URI
   pointing towards a valid manifest.

.. doctest::

   OwnedPackage = Package.from_uri('ipfs://QmbeVyFLSuEUxiXKwSsEjef6icpdTdA4kGG9BcrJXKNKUW', w3)

- To change the ``web3`` instance of a ``Package``.

.. doctest::

   >>> new_w3 = Web3(Web3.EthereumTesterProvider())
   >>> OwnedPackage.set_default_w3(new_w3)
   >>> assert OwnedPackage.w3 == new_w3

The following properties are available on a ``Package`` object.

.. doctest::
   
   >>> OwnedPackage.name
   'owned'
   >>> OwnedPackage.version
   '1.0.0'
   >>> OwnedPackage.manifest_version
   '2'
   >>> OwnedPackage.__repr__()
   '<Package owned==1.0.0>'

Contract Factories
------------------

Contract factories should be accessible from the package class.

.. code:: python

   Owned = OwnedPackage.get_contract_factory('owned')

In cases where a contract uses a library, the contract factory will have
unlinked bytecode. The ``ethpm`` package ships with its own subclass of
``web3.contract.Contract`` with a few extra methods and properties
related to bytecode linking.

.. code:: python

   >>> math = owned_package.contract_factories.math
   >>> math.has_linkable_bytecode
   True
   >>> math.is_bytecode_linked
   False
   >>> linked_math = math.link_bytecode({'MathLib': '0x1234...'})
   >>> linked_math.is_bytecode_linked
   True

..

   Note: the actual format of the link data is not clear since library
   names aren’t a one-size-fits all solution. We need the ability to
   specify specific link references in the code.


Contract Instances
------------------

To return a contract instance of a contract type belonging to a ``Package``.

.. code:: python
   
   owned = OwnedPackage.get_contract_instance('owned', '0x123...')


Deployments
-----------

Deployed contracts are only available from package instances. The
package instance will filter the ``deployments`` based on the chain that
``web3`` is connected to.

Accessing deployments is done with property access

.. code:: python

   package.deployed_contracts.Greeter


Dependencies
------------

The ``Package`` class should provide access to the full dependency tree.

.. code:: python

   >>> owned_package.build_dependencies['zeppelin']
   <ZeppelinPackage>


Validation
----------

The ``Package`` class currently verifies the following things.

-  Manifests used to instantiate a ``Package`` object conform to the `EthPM V2 Manifest Specification <https://github.com/ethpm/ethpm-spec/blob/master/spec/package.spec.json>`__

And in the future should verify.

-  Included bytecode matches compilation output
-  Deployed bytecode matches compilation output
