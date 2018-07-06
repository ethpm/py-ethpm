URI Schemes and Backends
========================

Registry URI
------------

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
