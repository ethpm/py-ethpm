import copy
import json
import pytest


LOCKFILE = {
  "lockfile_version": "1",
  "version": "1.0.0",
  "package_name": "safe-math-lib",
  "contract_types": {
    "SafeMathLib": {
      "bytecode": "0x606060405234610000575b60a9806100176000396000f36504062dabbdf050606060405260e060020a6000350463a293d1e88114602e578063e6cb901314604c575b6000565b603a600435602435606a565b60408051918252519081900360200190f35b603a6004356024356088565b60408051918252519081900360200190f35b6000828211602a57508082036081566081565b6000565b5b92915050565b6000828284011115602a57508181016081566081565b6000565b5b9291505056",
      "runtime_bytecode": "0x6504062dabbdf050606060405260e060020a6000350463a293d1e88114602e578063e6cb901314604c575b6000565b603a600435602435606a565b60408051918252519081900360200190f35b603a6004356024356088565b60408051918252519081900360200190f35b6000828211602a57508082036081566081565b6000565b5b92915050565b6000828284011115602a57508181016081566081565b6000565b5b9291505056",
      "compiler": {
        "type": "solc",
        "version": "0.4.6+commit.2dabbdf0.Darwin.appleclang",
        "settings": {
            "optimize": True
        }
      }
    }
  },
  "deployments": {
    "blockchain://41941023680923e0fe4d74a34bdac8141f2540e3ae90623718e47d66d1ca4a2d/block/1e96de11320c83cca02e8b9caf3e489497e8e432befe5379f2f08599f8aecede": {
      "SafeMathLib": {
        "contract_type": "SafeMathLib",
        "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
        "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
        "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c"
      }
    }
  }
}

@pytest.fixture
def lockfile_with_matching_deployments(tmpdir):
    f = tmpdir.join("lockfile.json")
    f.write(json.dumps(LOCKFILE))
    return str(f)


@pytest.fixture
def lockfile_with_no_deployments(tmpdir):
    lockfile = copy.deepcopy(LOCKFILE)
    lockfile.pop("deployments")
    f = tmpdir.join("lockfile.json")
    f.write(json.dumps(lockfile))
    return str(f)


@pytest.fixture
def lockfile_with_conflicting_deployments(tmpdir):
    lockfile = copy.deepcopy(LOCKFILE)
    lockfile["deployments"]["blockchain://41941023680923e0fe4d74a34bdac8141f2540e3ae90623718e47d66d1ca4a2d/block/1e96de11320c83cca02e8b9caf3e489497e8e432befe5379f2f08599f8aecede"] = {
      "WrongNameLib": {
        "contract_type": "SafeMathLib",
        "address": "0x8d2c532d7d211816a2807a411f947b211569b68c",
        "transaction": "0xaceef751507a79c2dee6aa0e9d8f759aa24aab081f6dcf6835d792770541cb2b",
        "block": "0x420cb2b2bd634ef42f9082e1ee87a8d4aeeaf506ea5cdeddaa8ff7cbf911810c"
      }
    }
    f = tmpdir.join("lockfile.json")
    f.write(json.dumps(lockfile))
    return str(f)
