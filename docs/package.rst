Packages
========

The ``Package`` object will function much like the ``Contract`` class
provided by ``web3``. Rather than instantiating the base class provided
by ``ethpm``, you will instead use a ``classmethod`` which generates a
new ``Package`` class for a given package.

-  Creating a ``Package`` object from a local manifest file.

.. code:: python

   OwnedPackage = Package.from_file('/path/to/owned-v1.0.0.json')

-  Creating a ``Package`` object from an IPFS URI pointing to a manifest
   file.

.. code:: python

   OwnedPackage = Package.from_ipfs('ipfs://QmbeVyFLSuEUxiXKwSsEjef6icpdTdA4kGG9BcrJXKNKUW')

-  Creating a ``Package`` object from a valid Registry URI.

.. code:: python

   OwnedPackage = Package.from_registry('ercXXX://example.packages.eth/owned?version=1.0.0')

Then, the ``OwnedPackage`` can be instantiated with any ``web3``
intance.

.. code:: python

   owned_package = OwnedPackage.set_default_w3(w3)

Contract Factories
------------------

Contract factories should be accessible from the package class, but the
``Package`` class must also have a set ``web3`` instance.

.. code:: python

   Owned = OwnedPackage.get_contract_type('owned', w3)

In cases where a contract uses a library, the contract factory will have
unlinked bytecode. The ``ethpm`` package ships with its own subclass of
``web3.contract.Contract`` with a few extra methods and properties
related to bytecode linking

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

Deployed Contracts
------------------

Deployed contracts are only available from package instances. The
package instance will filter the ``deployments`` based on the chain that
``web3`` is connected to.

Accessing deployments is done with property access

.. code:: python

   package.deployed_contracts.Greeter

Validation
----------

The ``Package`` class currently verifies the following things.

-  Package Manifest matches `EthPM V2 Manifest Specification <https://github.com/ethpm/ethpm-spec/blob/master/spec/package.spec.json>`__

And in the future should verify.

-  Included bytecode matches compilation output
-  Deployed bytecode matches compilation output

Dependencies
------------

The ``Package`` class should provide access to the full dependency tree.

.. code:: python

   >>> owned_package.build_dependencies['zeppelin']
   <ZeppelinPackage>

Testing Strategy
----------------

-  Load and validate packages from disk.
-  Access package data.
-  Access contract factories.

EthPM-Spec
----------

-  `EthPM-Spec <https://github.com/ethpm/ethpm-spec>`__ is referenced
   inside this repo as a submodule.*\*
-  If you clone this repository, you should run this command to fetch
   the contents of the submodule

.. code:: sh

   git submodule init
