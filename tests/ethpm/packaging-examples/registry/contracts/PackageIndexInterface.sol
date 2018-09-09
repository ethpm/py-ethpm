pragma solidity ^0.4.24;
pragma experimental "v0.5.0";


import {AuthorizedInterface} from "./Authority.sol";


/// @title Database contract for a package index.
/// @author Tim Coulter <tim.coulter@consensys.net>, Piper Merriam <pipermerriam@gmail.com>
contract PackageIndexInterface is AuthorizedInterface {
  //
  // Events
  //
  event PackageRelease(bytes32 indexed nameHash, bytes32 indexed releaseHash);
  event PackageTransfer(address indexed oldOwner, address indexed newOwner);

  //
  // Administrative API
  //
  /// @dev Sets the address of the PackageDb contract.
  /// @param newPackageDb The address to set for the PackageDb.
  function setPackageDb(address newPackageDb) public returns (bool);

  /// @dev Sets the address of the ReleaseDb contract.
  /// @param newReleaseDb The address to set for the ReleaseDb.
  function setReleaseDb(address newReleaseDb) public returns (bool);

  /// @dev Sets the address of the ReleaseValidator contract.
  /// @param newReleaseValidator The address to set for the ReleaseValidator.
  function setReleaseValidator(address newReleaseValidator) public returns (bool);

  //
  // +-------------+
  // |  Write API  |
  // +-------------+
  //
  /// @dev Creates a a new release for the named package.  If this is the first release for the given package then this will also assign msg.sender as the owner of the package.  Returns success.
  /// @notice Will create a new release the given package with the given release information.
  /// @param name Package name
  /// @param major The major portion of the semver version string.
  /// @param minor The minor portion of the semver version string.
  /// @param patch The patch portion of the semver version string.
  /// @param preRelease The pre-release portion of the semver version string.  Use empty string if the version string has no pre-release portion.
  /// @param build The build portion of the semver version string.  Use empty string if the version string has no build portion.
  /// @param manifestURI The URI for the release manifest for this release.
  function release(
    string name,
    uint32 major,
    uint32 minor,
    uint32 patch,
    string preRelease,
    string build,
    string manifestURI
  )
    public
    returns (bool);

  /// @dev Transfers package ownership to the provider new owner address.
  /// @notice Will transfer ownership of this package to the provided new owner address.
  /// @param name Package name
  /// @param newPackageOwner The address of the new owner.
  function transferPackageOwner(string name, address newPackageOwner) public returns (bool);

  //
  // +------------+
  // |  Read API  |
  // +------------+
  //

  /// @dev Returns the address of the packageDb
  function getPackageDb() public view returns (address);

  /// @dev Returns the address of the releaseDb
  function getReleaseDb() public view returns (address);

  /// @dev Returns the address of the releaseValidator
  function getReleaseValidator() public view returns (address);

  /// @dev Query the existence of a package with the given name.  Returns boolean indicating whether the package exists.
  /// @param name Package name
  function packageExists(string name) public view returns (bool);

  /// @dev Query the existence of a release at the provided version for the named package.  Returns boolean indicating whether such a release exists.
  /// @param name Package name
  /// @param major The major portion of the semver version string.
  /// @param minor The minor portion of the semver version string.
  /// @param patch The patch portion of the semver version string.
  /// @param preRelease The pre-release portion of the semver version string.  Use empty string if the version string has no pre-release portion.
  /// @param build The build portion of the semver version string.  Use empty string if the version string has no build portion.
  function releaseExists(
    string name,
    uint32 major,
    uint32 minor,
    uint32 patch,
    string preRelease,
    string build
  )
    public
    view
    returns (bool);

  /// @dev Returns the number of packages in the index
  function getNumPackages() public view returns (uint);

  /// @dev Returns the name of the package at the provided index
  /// @param idx The index of the name hash to lookup.
  function getPackageName(uint idx) public view returns (string);

  /// @dev Returns the package data.
  /// @param name Package name
  function getPackageData(string name)
    public
    view
    returns (
      address packageOwner,
      uint createdAt,
      uint numReleases,
      uint updatedAt
    );

  /// @dev Returns the release data for the release associated with the given release hash.
  /// @param releaseHash The release hash.
  function getReleaseData(bytes32 releaseHash)
    public
    view
    returns (
      uint32 major,
      uint32 minor,
      uint32 patch,
      string preRelease,
      string build,
      string manifestURI,
      uint createdAt,
      uint updatedAt
    );

  /// @dev Returns the release hash at the provide index in the array of all release hashes.
  /// @param idx The index of the release to retrieve.
  function getReleaseHash(uint idx) public view returns (bytes32);

  /// @dev Returns the release hash at the provide index in the array of release hashes for the given package.
  /// @param name Package name
  /// @param releaseIdx The index of the release to retrieve.
  function getReleaseHashForPackage(string name, uint releaseIdx) public view returns (bytes32);

  /// @dev Returns an array of all release hashes for the named package.
  /// @param name Package name
  function getAllPackageReleaseHashes(string name) public view returns (bytes32[]);

  /// @dev Returns a slice of the array of all release hashes for the named package.
  /// @param name Package name
  /// @param offset The starting index for the slice.
  /// @param numReleases The length of the slice
  function getPackageReleaseHashes(
    string name,
    uint offset,
    uint numReleases
  )
    public
    view
    returns (bytes32[]);

  function getNumReleases() public view returns (uint);

  /// @dev Returns an array of all release hashes for the named package.
  function getAllReleaseHashes() public view returns (bytes32[]);

  /// @dev Returns a slice of the array of all release hashes for the named package.
  /// @param offset The starting index for the slice.
  /// @param numReleases The length of the slice
  function getReleaseHashes(uint offset, uint numReleases) public view returns (bytes32[]);

  /// @dev Returns the release manifest for the given release data
  /// @param name Package name
  /// @param major The major portion of the semver version string.
  /// @param minor The minor portion of the semver version string.
  /// @param patch The patch portion of the semver version string.
  /// @param preRelease The pre-release portion of the semver version string.  Use empty string if the version string has no pre-release portion.
  /// @param build The build portion of the semver version string.  Use empty string if the version string has no build portion.
  function getReleaseManifestURI(
    string name,
    uint32 major,
    uint32 minor,
    uint32 patch,
    string preRelease,
    string build
  )
    public
    view
    returns (string);
}
