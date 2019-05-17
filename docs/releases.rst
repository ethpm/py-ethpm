Release Notes
=============

v0.1.4-alpha.16
---------------

Released May 17th, 2019

- Update to use new IPFS library
  - `#158 <https://github.com/ethpm/py-ethpm/pull/158>`_

- Update mypy dependency
  - `#153 <https://github.com/ethpm/py-ethpm/pull/153>`_

v0.1.4-alpha.15
---------------

Released April 25th, 2019

- Write is_supported_content_addressed_uri util.
    - `#152 <https://github.com/ethpm/py-ethpm/pull/152>`_

v0.1.4-alpha.14
---------------

Released April 10th, 2019

- Bugfix

  - Update registry backend to work with ``web3.pm``
    - `#151 <https://github.com/ethpm/py-ethpm/pull/151>`_

v0.1.4-alpha.13
---------------

Released March 22nd, 2019

- Bugfix

  - Remove auto infura endpoint
    - `#149 <https://github.com/ethpm/py-ethpm/pull/149>`_

v0.1.4-alpha.12
---------------

Released February 12th, 2019

- Breaking Changes

  - Change ``Package.switch_w3`` to ``Package.update_w3``
    - `#146 <https://github.com/ethpm/py-ethpm/pull/146>`_

v0.1.4-alpha.11
---------------

Released February 12th, 2019

- Breaking Changes

  - Remove ``py-solc`` dependency and solidity compilation
    - `#143 <https://github.com/ethpm/py-ethpm/pull/143>`_
  - Update vyper reference registry assets
    - `#145 <https://github.com/ethpm/py-ethpm/pull/145>`_

- Features

  - Support contract aliasing for deployments
    - `#144 <https://github.com/ethpm/py-ethpm/pull/144>`_


v0.1.4-alpha.10
---------------

Released January 17th, 2019

- Breaking Changes

  - ``Package.set_default_w3()`` returns new ``Package``
    instance.
    - `#139 <https://github.com/ethpm/py-ethpm/pull/139>`_
  - ``Web3`` dependency updated to ``v5.0.0a3``.
    - `#137 <https://github.com/ethpm/py-ethpm/pull/137>`_

- Bugfixes

  - ``Builder`` bugfix to account for contract factories.
    - `#138 <https://github.com/ethpm/py-ethpm/pull/138>`_
  - Add ``global_doctest_setup`` for autodoc to use.
