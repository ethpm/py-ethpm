Release Notes
=============

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
