# Py-EthPM

[![Join the chat at https://gitter.im/ethpm/lobby](https://badges.gitter.im/ethpm/lobby.py.svg)](https://gitter.im/ethpm/lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![CircleCI](https://circleci.com/gh/ethpm/py-ethpm.svg?style=svg)](https://circleci.com/gh/ethpm/py-ethpm)
[![PyPI version](https://badge.fury.io/py/ethpm.svg)](https://badge.fury.io/py/ethpm)

A Python implementation of the [Ethereum Package Manager Specification](http://ethpm.github.io/ethpm-spec/package-spec.html).

Read more in the documentation on [ReadTheDocs](https://py-ethpm.readthedocs.io/en/latest/).

WARNING!

`Py-EthPM` is currently in public alpha. *Keep in mind*:
- It is expected to have bugs and is not meant to be used in production
- Things may be ridiculously slow or not work at all

## Quickstart
```sh
pip install ethpm
```

## Developer Setup

If you would like to hack on Py-EthPM, please check out the
[Ethereum Development Tactical Manual](https://github.com/pipermerriam/ethereum-dev-tactical-manual)
for information on how we do:

- Testing
- Pull Requests
- Code Style
- Documentation

### Developer Environment Setup

You can set up your dev environment with:

```sh
git clone git@github.com:ethpm/py-ethpm.git
cd py-ethpm
virtualenv -p python3 venv
. venv/bin/activate
pip install -e .[dev]
```

### Testing Setup

During development, you might like to have tests run on every file save.

Show flake8 errors on file change:

```sh
# Test flake8
when-changed -v -s -r -1 py-ethpm/ tests/ -c "clear; flake8 py-ethpm tests && echo 'flake8 success' || echo 'error'"
```

Run multi-process tests in one command, but without color:

```sh
# in the project root:
pytest --numprocesses=4 --looponfail --maxfail=1
# the same thing, succinctly:
pytest -n 4 -f --maxfail=1
```

Run in one thread, with color and desktop notifications:

```sh
cd venv
ptw --onfail "notify-send -t 5000 'Test failure ⚠⚠⚠⚠⚠' 'python 3 test on <REPO_NAME> failed'" ../tests ../<MODULE_NAME>
```

#### How to Execute the Tests?

1. [Setup your development environment](https://github.com/ethpm/py-ethpm/#developer-setup).

2. Execute `tox` for the tests

There are multiple [components](https://github.com/ethpm/py-ethpm/blob/master/.circleci/.config.yml#L56) of the tests. You can run test to against specific component. For example:

```sh
# Run Tests for the Core component (for Python 3.5):
tox -e py35

# Run Tests for the Core component (for Python 3.6):
tox -e py36
```

If for some reason it is not working, add `--recreate` params.

`tox` is good for testing against the full set of build targets. But if you want to run the tests individually, `py.test` is better for development workflow. For example, to run only the tests in one file:

```sh
pytest tests/ethpm/utils/test_uri_utils.py
```

IPFS integration tests (`tests/ethpm/integration/`) require a direct connection to an IPFS node and are skipped by default (except in CircleCI, where they are run). To include these tests in your test run, first start an IPFS node and then add `--integration` to the pytest command.

### Release setup

For Debian-like systems:
```
apt install pandoc
```

To release a new version:

```sh
make release bump=$$VERSION_PART_TO_BUMP$$
```

#### How to bumpversion

The version format for this repo is `{major}.{minor}.{patch}` for stable, and
`{major}.{minor}.{patch}-{stage}.{devnum}` for unstable (`stage` can be alpha or beta).

To issue the next version in line, specify which part to bump,
like `make release bump=minor` or `make release bump=devnum`.

If you are in a beta version, `make release bump=stage` will switch to a stable.

To issue an unstable version when the current version is stable, specify the
new version explicitly, like `make release bump="--new-version 4.0.0-alpha.1 devnum"`

### EthPM-Spec

-  `EthPM-Spec <https://github.com/ethpm/ethpm-spec>`__ is referenced
   inside this repo as a submodule.*\*
-  If you clone this repository, run this command to fetch
   the contents of the submodule

```
   git submodule init
```
