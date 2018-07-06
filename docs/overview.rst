Overview
========

This is a Python implementation of the `Ethereum Smart Contract
Packaging
Specification <http://ethpm.github.io/ethpm-spec/package-spec.html>`__,
driven by discussions in `ERC
190 <https://github.com/ethereum/EIPs/issues/190>`__ and `ERC
1123 <https://github.com/ethereum/EIPs/issues/1123>`__.

WARNING 

``Py-EthPM`` is currently in public alpha. *Keep in mind*: 

- It is expected to have bugs and is not meant to be used in production 
- Things may be ridiculously slow or not work at all

``Py-EthPM`` is being built out to: 

- Parse and validate packages. 
- Provide access to contract factory classes (given a ``web3`` instance).
- Provide access to all of the deployed contract instances on a chain (given a connected ``web3`` instance). 
- Validate package bytecode matches compilation output. 
- Validate deployed bytecode matches compilation output. 
- Access to package’s dependencies. 
- Construct and publish new packages.
