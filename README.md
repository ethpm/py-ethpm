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


## EthPM-Spec

* [EthPM-Spec](https://github.com/ethpm/ethpm-spec) is referenced inside this repo as a submodule.**
* If you clone this repository, you should run this command to fetch the contents of the submodule
```sh
git submodule init
```

## Registry URI 

The URI to lookup a package from a registry should follow the following format. (subject to change as the Registry Contract Standard makes it's way through the EIP process)

```
scheme://authority/package-name?version=x.x.x
```

* URI must be a string type
* `scheme`: `ercxxx` 
* `authority`: Must be a valid ENS domain or a valid checksum address pointing towards a registry contract.
* `package-name`: Must conform to the package-name as specified in the [EthPM-Spec](http://ethpm-spec.readthedocs.io/en/latest/package-spec.html#package-name).
* `version`: The URI escaped version string, *should* conform to the [semver](http://semver.org/) version numbering specification.

i.e. `ercxxx://packages.zeppelinos.eth/owned?version=1.0.0`


## Release setup
For Debian-like systems:

```sh
apt install pandoc
```

To release a new version:

```sh
make release bump=$$VERSION_PART_TO_BUMP$$
```

## How to bumpversion
The version format for this repo is `{major}.{minor}.{patch}` for stable, and `{major}.{minor}.{patch}-{stage}.{devnum}` for unstable (`stage` can be alpha or beta).

To issue the next version in line, specify which part to bump, like `make release bump=minor` or `make release bump=devnum`.

If you are in a beta version, `make release bump=stage` will switch to a stable.

To issue an unstable version when the current version is stable, specify the new version explicitly, like `make release bump="--new-version 4.0.0-alpha.1 devnum"`
