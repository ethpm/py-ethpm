# ETHPM

* parse and validate packages.
* given a web3 instance provide access to contract factory classes
* given a web3 instance provide access to all of the deployed contract instances for the chain that web3 is connected to.
* validate package bytecode matches compilation output.
* validate deployed bytecode matches compilation output
* access to packages dependencies
* construct new packages 


## Web3

The `Package` object will function much like the `Contract` class provided by `web3`.  Rather than instantiating the base class provided by `ethpm`, you will instead use a `classmethod` which generates a new `Package` class for a given package.

```python
OwnedPackage = BasePackage.factory('/path/to/owned-v1.0.0.json')
```

Then, the `OwnedPackage` can be instantiated with any `web3` intance.

```python
owned_package = OwnedPackage(web3)
```

A `Package` class can only be directly constructed from the parsed package JSON. It can also be initialized with the package's URI or the local filesystem path to a package by using `Package.from_file(path)`.


## Contract Factories

Contract factories should be accessible from the package class but you must
also provide a web3 instance.

```python
Owned = OwnedPackage.get_contract_factory(web3, 'owned')
```

From a package instance, they are also available as properties.

```python
Owned = owned_package.contract_factories.owned
```

In cases where a contract uses a library, the contract factory will have
unlinked bytecode.  The `ethpm` package ships with its own subclass of
`web3.contract.Contract` with a few extra methods and properties related to
bytecode linking


```python
>>> math = owned_package.contract_factories.math
>>> math.has_linkable_bytecode
True
>>> math.is_bytecode_linked
False
>>> linked_math = math.link_bytecode({'MathLib': '0x1234...'})
>>> linked_math.is_bytecode_linked
True
```

> Note: the actual format of the link data is not clear since library names
> aren't a one-size-fits all solution.  We need the ability to specify specific
> link references in the code.


## Deployed Contracts

Deployed contracts are only available from package instances.  The package
instance will filter the `deployments` based on the chain that `web3` is
connected to.

Accessing deployments is done with property access

```python
package.deployed_contracts.Greeter
```


## IPFS

We'll need a pluggable backend system for IPFS access.  A built-in default one
that defaults to using infura should be enough to get off the ground.

Lower priority but important will be ensuring that a user can configure
connecting to their own IPFS node.


## Verifying Things

The `Package` class should verify all of the following things.

* Package json matches EthPM V2 Manifest Specification
* Included bytecode matches compilation output
* Deployed bytecode matches compilation output

    
## Dependencies

The `Package` class should provide access to the full dependency tree.

```python
>>> owned_package.build_dependencies['zeppelin']
<ZeppelinPackage>
```
    

## Testing Strategy

* Load and validate packages from disk.
* Access package data.
* Access contract factories.
