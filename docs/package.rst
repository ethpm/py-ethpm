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

.. autoclass:: ethpm.Package
   :members: name, version, manifest_version, uri, __repr__, build_dependencies, deployments

.. py:attribute:: Package.w3

   The ``Web3`` instance currently set on this ``Package``. The deployments available on a package are automatically filtered to only contain those belonging to the currently set ``w3`` instance.

.. py:attribute:: Package.manifest

   The manifest dict used to instantiate a ``Package``.


Methods
-------

Each ``Package`` exposes the following methods.

.. autoclass:: ethpm.Package
   :members: from_file, from_uri, update_w3, get_contract_factory, get_contract_instance


Validation
----------

The ``Package`` class currently verifies the following things.

-  Manifests used to instantiate a ``Package`` object conform to the `EthPM V2 Manifest Specification <https://github.com/ethpm/ethpm-spec/blob/master/spec/package.spec.json>`__

And in the future should verify.

-  Included bytecode matches compilation output
-  Deployed bytecode matches compilation output
