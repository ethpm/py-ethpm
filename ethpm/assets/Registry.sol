pragma solidity 0.4.24;

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
