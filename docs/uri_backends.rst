URI Schemes and Backends
========================

BaseURIBackend
--------------

``Py-EthPM`` uses the ``BaseURIBackend`` as the parent class for all of its URI backends. To write your own backend, it must implement the following methods. 

.. py:method:: BaseURIBackend.can_resolve_uri(uri)

   Return a bool indicating whether or not this backend is capable of resolving the given URI to a manifest.
   A content-addressed URI pointing to valid manifest is said to be capable of "resolving".

.. py:method:: BaseURIBackend.can_translate_uri(uri)

   Return a bool indicating whether this backend class can translate the given URI to a corresponding content-addressed URI.
   A registry URI is said to be capable of "transalating" if it points to another content-addressed URI in its respective on-chain registry.

.. py:method:: BaseURIBackend.fetch_uri_contents(uri)

   Fetch the contents stored at the provided uri, if an available backend is capable of resolving the URI. Validates that contents stored at uri match the content hash suffixing the uri.


IPFS
----

``Py-EthPM`` has multiple backends available to fetch/pin files to IPFS. The desired backend can be set via the environment variable: ``ETHPM_IPFS_BACKEND_CLASS``.

- ``InfuraIPFSBackend`` (default)
    - `https://ipfs.infura.io`
- ``IPFSGatewayBackend`` (temporarily deprecated)
    - `https://ipfs.io/ipfs/`
- ``LocalIPFSBacked``
    - Connect to a local IPFS API gateway running on port 5001.
- ``DummyIPFSBackend``
    - Won't pin/fetch files to an actual IPFS node, but mocks out this behavior.

.. py:method:: BaseIPFSBackend.pin_assets(file_or_directory_path)

   Pin asset(s) found at the given path and returns the pinned asset data.


HTTPS
-----

``Py-EthPM`` offers a backend to fetch files from Github, ``GithubOverHTTPSBackend``.

A valid content-addressed Github URI *must* conform to the following scheme, as described in `ERC1319 <https://github.com/ethereum/EIPs/issues/1319>`__, to be used with this backend.

.. code:: python

   https://api.github.com/repos/:owner/:repo/git/blobs/:file_sha


.. py:method:: create_content_addressed_github_uri(uri)

   This util function will return a content-addressed URI, as defined by Github's `blob <https://developer.github.com/v3/git/blobs/>`__ scheme. To generate a content-addressed URI for any manifest stored on github, this function requires accepts a Github API uri that follows the following scheme.

::
  
   https://api.github.com/repos/:owner/:repo/contents/:path/:to/manifest.json

.. doctest::

   >>> from ethpm.utils.uri import create_content_addressed_github_uri

   >>> owned_github_api_uri = "https://api.github.com/repos/ethpm/py-ethpm/contents/ethpm/assets/owned/1.0.1.json"
   >>> content_addressed_uri = "https://api.github.com/repos/ethpm/py-ethpm/git/blobs/a7232a93f1e9e75d606f6c1da18aa16037e03480"

   >>> actual_blob_uri = create_content_addressed_github_uri(owned_github_api_uri)
   >>> assert actual_blob_uri == content_addressed_uri


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
