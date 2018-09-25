URI Schemes and Backends
========================

IPFS
----

``Py-EthPM`` has multiple backends available to fetch/pin files to IPFS. The desired backend can be set via the environment variable: ``ETHPM_IPFS_BACKEND_CLASS``.

- ``InfuraIPFSBackend`` (default)
    - `https://ipfs.infura.io`
- ``IPFSGatewayBackend``
    - `https://ipfs.io/ipfs/`
- ``LocalIPFSBacked``
    - connects to a local IPFS API gateway running on port 5001.
- ``DummyIPFSBackend``
    - Won't pin/fetch files to an actual IPFS node, but mocks out this behavior.

.. py:method:: BaseIPFSBackend.can_resolve_uri(uri)

   Returns a bool indicating whether or not this backend is capable of handling the given URI.

.. py:method:: BaseIPFSBackend.fetch_uri_contents(uri)

   Fetches the contents stored at a URI.

.. py:method:: BaseIPFSBackend.pin_assets(file_or_directory_path)

   Pins asset(s) found at the given path and returns the pinned asset data.

Registry URIs
-------------

The URI to lookup a package from a registry should follow the following
format. (subject to change as the Registry Contract Standard makes it’s
way through the EIP process)

::

   scheme://authority/package-name?version=x.x.x

-  URI must be a string type
-  ``scheme``: ``ercxxx``
-  ``authority``: Must be a valid ENS domain or a valid checksum address
   pointing towards a registry contract.
-  ``package-name``: Must conform to the package-name as specified in
   the
   `EthPM-Spec <http://ethpm-spec.readthedocs.io/en/latest/package-spec.html#package-name>`__.
-  ``version``: The URI escaped version string, *should* conform to the
   `semver <http://semver.org/>`__ version numbering specification.

i.e. ``ercxxx://packages.zeppelinos.eth/owned?version=1.0.0``
