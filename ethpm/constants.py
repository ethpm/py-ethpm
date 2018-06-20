# TODO update once registry standard eip has been approved
REGISTRY_URI_SCHEME = 'ercxxx'

PACKAGE_NAME_REGEX = '[a-zA-Z][-_a-zA-Z0-9]{0,255}'


#
# Sample Registry Contract
# TODO: Update once Registry Contract Standard ERC is finalized
#
REGISTRY_SOURCE = '''
pragma solidity 0.4.23;

contract Registry {
    mapping (bytes32 => Package) public index;

    struct Package {
        string uri;
        string version;
    }

    function registerPackage(bytes32 _name, string _version, string _uri) public {
        index[_name] = Package(_uri, _version);
    }

    function lookupPackage(bytes32 _name) public view returns (string) {
        return index[_name].uri;
    }

}
'''
REGISTRY_ABI = '''
[
        {
                "constant": true,
                "inputs": [
                        {
                                "name": "_name",
                                "type": "bytes32"
                        }
                ],
                "name": "lookupPackage",
                "outputs": [
                        {
                                "name": "",
                                "type": "string"
                        }
                ],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
        },
        {
                "constant": true,
                "inputs": [
                        {
                                "name": "",
                                "type": "bytes32"
                        }
                ],
                "name": "index",
                "outputs": [
                        {
                                "name": "uri",
                                "type": "string"
                        },
                        {
                                "name": "version",
                                "type": "string"
                        }
                ],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
        },
        {
                "constant": false,
                "inputs": [
                        {
                                "name": "_name",
                                "type": "bytes32"
                        },
                        {
                                "name": "_version",
                                "type": "string"
                        },
                        {
                                "name": "_uri",
                                "type": "string"
                        }
                ],
                "name": "registerPackage",
                "outputs": [],
                "payable": false,
                "stateMutability": "nonpayable",
                "type": "function"
        }
]
'''
