Package
=======

The ``Package`` object will function much like the ``Contract`` class
provided by ``web3``. Rather than instantiating the base class provided
by ``ethpm``, you will instead use a ``classmethod`` which generates a
new ``Package`` class for a given package.

``Package`` objects *must* be instantiated with a valid ``web3`` object.

.. doctest::
  
   >>> from ethpm import Package, V2_PACKAGES_DIR
   >>> from web3 import Web3

   >>> owned_manifest_path = V2_PACKAGES_DIR / 'owned' / '1.0.0.json'
   >>> w3 = Web3(Web3.EthereumTesterProvider())

   >>> OwnedPackage = Package.from_file(owned_manifest_path, w3)
   >>> assert isinstance(OwnedPackage, Package)

Properties
----------

Each ``Package`` exposes the following properties.

.. py:attribute:: Package.w3

   The ``Web3`` instance currently set on this ``Package``. The deployments available on a package are automatically filtered to only contain those belonging to the currently set ``w3`` instance.

.. py:attribute:: Package.manifest

   The manifest dict used to instantiate a ``Package``.

.. py:attribute:: Package.name

   The name of this ``Package``.

.. doctest::
   
   >>> OwnedPackage.name
   'owned'

.. py:attribute:: Package.version

   The package version of a ``Package``.

.. doctest::

   >>> OwnedPackage.version
   '1.0.0'

.. py:attribute:: Package.manifest_version

   The manifest version of a ``Package``.

.. doctest::

   >>> OwnedPackage.manifest_version
   '2'

.. py:attribute:: Package.__repr__()

.. doctest::

   >>> OwnedPackage.__repr__()
   '<Package owned==1.0.0>'

.. py:attribute:: Package.build_dependencies

   A ``Dependencies`` object containing ``Package`` instances for all `build_dependencies` present in a ``Package``'s manifest. This is a `cached_property` that is busted everytime a ``Package``'s ``Web3`` instance is changed via ``Package.set_default_w3()``. The ``Package`` class should provide access to the full dependency tree.

.. code:: python

   >>> owned_package.build_dependencies['zeppelin']
   <ZeppelinPackage>

.. py:attribute:: Package.deployments

   A ``Deployments`` object containing all the deployment data and contract factories of a ``Package``'s `contract_types`. Automatically filters deployments to only expose those available on the current ``Package.w3`` instance. This is a `cached_property` that is busted everytime a ``Package``'s ``Web3`` instance is changed via ``Package.set_default_w3()``.

.. code:: python

   package.deployments.Greeter

Methods
-------

.. py:classmethod:: Package.from_file(file_path, w3)

   This classmethod is provided to instantiate a ``Package`` from a local file. ``file_path`` arg must be a `pathlib.Path` instance. A valid ``Web3`` instance is also required to instantiate a ``Package``.

.. py:classmethod:: Package.from_uri(uri, w3)
  
   This classmethod is provided to instantiate a ``Package`` from a valid content-addressed URI. A valid ``Web3`` instance is also required to instantiate a ``Package``.

.. code:: python

   OwnedPackage = Package.from_uri('ipfs://QmbeVyFLSuEUxiXKwSsEjef6icpdTdA4kGG9BcrJXKNKUW', w3)

.. py:method:: Package.set_default_w3(w3)

   Will update the current ``web3`` instance belonging to a ``Package``. This will also bust the `cached_properties` ``Package.build_dependencies`` and ``Package.deployments``.

.. doctest::

   >>> new_w3 = Web3(Web3.EthereumTesterProvider())
   >>> OwnedPackage.set_default_w3(new_w3)
   >>> assert OwnedPackage.w3 == new_w3


.. py:method:: Package.get_contract_factory(name)

   Will return the contract factory for a given contract type, generated from the data vailable in ``Package.manifest``. Contract factories are accessible from the package class.

.. code:: python

   Owned = OwnedPackage.get_contract_factory('owned')

In cases where a contract uses a library, the contract factory will have
unlinked bytecode. The ``ethpm`` package ships with its own subclass of
``web3.contract.Contract`` with a few extra methods and properties
related to bytecode linking.

.. code:: python

   >>> math = owned_package.contract_factories.math
   >>> math.needs_bytecode_linking
   True
   >>> linked_math = math.link_bytecode({'MathLib': '0x1234...'})
   >>> linked_math.needs_bytecode_linking
   False

..

   Note: the actual format of the link data is not clear since library
   names aren’t a one-size-fits all solution. We need the ability to
   specify specific link references in the code.


.. py:method:: Package.get_contract_instance(name, address)

   Will return a ``Web3.contract`` instance generated from the contract type data available in ``Package.manifest`` and the provided ``address``. The provided ``address`` must be valid on the connected chain available through ``Package.w3``.


Validation
----------

The ``Package`` class currently verifies the following things.

-  Manifests used to instantiate a ``Package`` object conform to the `EthPM V2 Manifest Specification <https://github.com/ethpm/ethpm-spec/blob/master/spec/package.spec.json>`__

And in the future should verify.

-  Included bytecode matches compilation output
-  Deployed bytecode matches compilation output
