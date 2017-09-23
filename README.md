# ERC190

* parse and validate lockfiles.
* given a web3 instance provide access to contract factory classes
* given a web3 instance provide access to all of the deployed contract instances for the chain that web3 is connected to.
* validate package bytecode matches compilation output.
* validate deployed bytecode matches compilation output
* access to packages dependencies
* construct new lockfiles


## Contracts

Accessing contracts something like this.

```python
package.contract_factories.Greeter
```

> TODO: need to figure out how linking is going to work.

In order to accomodate linking this may need to be a method call.

```python
package.get_contract_factory('Greeter', link_values=....TODO...)
```

Also, it may make sense to make contract bytecode linking a first class feature
in web3.py so that we can do something like:

```python
>>> contract = web3.eth.contract('0x0001', ...)
>>> library_a = web3.eth.contract('0x0002', ...)

>>> linked_contract = contract.link({'LibraryA': library_a, 'LibraryB': '0x0003'})
>>> contract.is_linked
False
>>> linked_contract.is_linked
True
```


## Web3

* Needs to not be a single web3 instance.  Instead, user passes in many *named* ones like this.

```python
package.configure_web3('mainnet', web3_for_mainnet)
package.configure_web3('rinkeby', web3_for_rinkeby)
```

Then, to access deployed contracts:

```python
package.deployed_contracts.mainnet.Greeter
```


## Needed Backends

* IPFS
    

## Testing Strategy

* Load and validate lockfiles from disk.
* Access lockfile data.
* Access contract factories.
