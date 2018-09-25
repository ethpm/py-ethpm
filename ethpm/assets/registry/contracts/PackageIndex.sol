pragma solidity ^0.4.24;
pragma experimental "v0.5.0";


import {PackageDB} from "./PackageDB.sol";
import {ReleaseDB} from "./ReleaseDB.sol";
import {ReleaseValidator} from "./ReleaseValidator.sol";
import {PackageIndexInterface} from "./PackageIndexInterface.sol";
import {Authorized} from "./Authority.sol";


/// @title Database contract for a package index.
/// @author Tim Coulter <tim.coulter@consensys.net>, Piper Merriam <pipermerriam@gmail.com>
contract PackageIndex is Authorized, PackageIndexInterface {
  PackageDB private packageDb;
  ReleaseDB private releaseDb;
  ReleaseValidator private releaseValidator;

  //
  // Administrative API
  //
  /// @dev Sets the address of the PackageDb contract.
  /// @param newPackageDb The address to set for the PackageDb.
  function setPackageDb(address newPackageDb)
    public
    auth
    returns (bool)
  {
    packageDb = PackageDB(newPackageDb);
    return true;
  }

  /// @dev Sets the address of the ReleaseDb contract.
  /// @param newReleaseDb The address to set for the ReleaseDb.
  function setReleaseDb(address newReleaseDb)
    public
    auth
    returns (bool)
  {
    releaseDb = ReleaseDB(newReleaseDb);
    return true;
  }

  /// @dev Sets the address of the ReleaseValidator contract.
  /// @param newReleaseValidator The address to set for the ReleaseValidator.
  function setReleaseValidator(address newReleaseValidator)
    public
    auth
    returns (bool)
  {
    releaseValidator = ReleaseValidator(newReleaseValidator);
    return true;
  }

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
    auth
    returns (bool)
  {
    require(address(packageDb) != 0x0,        "escape:PackageIndex:package-db-not-set");
    require(address(releaseDb) != 0x0,        "escape:PackageIndex:release-db-not-set");
    require(address(releaseValidator) != 0x0, "escape:PackageIndex:release-validator-not-set");

    return release(name, [major, minor, patch], preRelease, build, manifestURI);
  }

  /// @dev Creates a a new release for the named package.  If this is the first release for the given package then this will also assign msg.sender as the owner of the package.  Returns success.
  /// @notice Will create a new release the given package with the given release information.
  /// @param name Package name
  /// @param majorMinorPatch The major/minor/patch portion of the version string.
  /// @param preRelease The pre-release portion of the semver version string.  Use empty string if the version string has no pre-release portion.
  /// @param build The build portion of the semver version string.  Use empty string if the version string has no build portion.
  /// @param manifestURI The URI for the release manifest for this release.
  function release(
    string name,
    uint32[3] majorMinorPatch,
    string preRelease,
    string build,
    string manifestURI
  )
    internal
    returns (bool)
  {
    bytes32 versionHash = releaseDb.hashVersion(
      majorMinorPatch[0],
      majorMinorPatch[1],
      majorMinorPatch[2],
      preRelease,
      build
    );

    // If the version for this release is not in the version database, populate
    // it.  This must happen prior to validation to ensure that the version is
    // present in the releaseDb.
    if (!releaseDb.versionExists(versionHash)) {
      releaseDb.setVersion(
        majorMinorPatch[0],
        majorMinorPatch[1],
        majorMinorPatch[2],
        preRelease,
        build
      );
    }

    // Run release validator. This method reverts with an error message string
    // on failure.
    releaseValidator.validateRelease(
      packageDb,
      releaseDb,
      msg.sender,
      name,
      majorMinorPatch,
      preRelease,
      build,
      manifestURI
    );

    // Compute hashes
    bool _packageExists = packageExists(name);

    // Both creates the package if it is new as well as updating the updatedAt
    // timestamp on the package.
    packageDb.setPackage(name);

    bytes32 nameHash = packageDb.hashName(name);

    // If the package does not yet exist create it and set the owner
    if (!_packageExists) {
      packageDb.setPackageOwner(nameHash, msg.sender);
    }

    // Create the release and add it to the list of package release hashes.
    releaseDb.setRelease(nameHash, versionHash, manifestURI);

    // Log the release.
    emit PackageRelease(nameHash, releaseDb.hashRelease(nameHash, versionHash));

    return true;
  }

  /// @dev Transfers package ownership to the provider new owner address.
  /// @notice Will transfer ownership of this package to the provided new owner address.
  /// @param name Package name
  /// @param newPackageOwner The address of the new owner.
  function transferPackageOwner(string name, address newPackageOwner)
    public
    auth
    returns (bool)
  {
    if (isPackageOwner(name, msg.sender)) {
      // Only the package owner may transfer package ownership.
      return false;
    }

    // Lookup the current owner
    address packageOwner;
    (packageOwner,,,) = getPackageData(name);

    // Log the transfer
    emit PackageTransfer(packageOwner, newPackageOwner);

    // Update the owner.
    packageDb.setPackageOwner(packageDb.hashName(name), newPackageOwner);

    return true;
  }

  //
  // +------------+
  // |  Read API  |
  // +------------+
  //

  /// @dev Returns the address of the packageDb
  function getPackageDb()
    public
    view
    returns (address)
  {
    return address(packageDb);
  }

  /// @dev Returns the address of the releaseDb
  function getReleaseDb()
    public
    view
    returns (address)
  {
    return address(releaseDb);
  }

  /// @dev Returns the address of the releaseValidator
  function getReleaseValidator()
    public
    view
    returns (address)
  {
    return address(releaseValidator);
  }

  /// @dev Query the existence of a package with the given name.  Returns boolean indicating whether the package exists.
  /// @param name Package name
  function packageExists(string name)
    public
    view
    returns (bool)
  {
    return packageDb.packageExists(packageDb.hashName(name));
  }

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
    returns (bool)
  {
    bytes32 nameHash = packageDb.hashName(name);
    bytes32 versionHash = releaseDb.hashVersion(major, minor, patch, preRelease, build);
    return releaseDb.releaseExists(releaseDb.hashRelease(nameHash, versionHash));
  }

  /// @dev Returns the number of packages in the index
  function getNumPackages()
    public
    view
    returns (uint)
  {
    return packageDb.getNumPackages();
  }

  /// @dev Returns the name of the package at the provided index
  /// @param idx The index of the name hash to lookup.
  function getPackageName(uint idx)
    public
    view
    returns (string)
  {
    return getPackageName(packageDb.getPackageNameHash(idx));
  }

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
    )
  {
    bytes32 nameHash = packageDb.hashName(name);
    (packageOwner, createdAt, updatedAt) = packageDb.getPackageData(nameHash);
    numReleases = releaseDb.getNumReleasesForNameHash(nameHash);
    return (packageOwner, createdAt, numReleases, updatedAt);
  }

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
    )
  {
    bytes32 versionHash;
    (,versionHash, createdAt, updatedAt) = releaseDb.getReleaseData(releaseHash);
    (major, minor, patch) = releaseDb.getMajorMinorPatch(versionHash);
    preRelease = getPreRelease(releaseHash);
    build = getBuild(releaseHash);
    manifestURI = getReleaseManifestURI(releaseHash);
    return (major, minor, patch, preRelease, build, manifestURI, createdAt, updatedAt);
  }

  /// @dev Returns the release hash at the provide index in the array of all release hashes.
  /// @param idx The index of the release to retrieve.
  function getReleaseHash(uint idx)
    public
    view
    returns (bytes32)
  {
    return releaseDb.getReleaseHash(idx);
  }

  /// @dev Returns the release hash at the provide index in the array of release hashes for the given package.
  /// @param name Package name
  /// @param releaseIdx The index of the release to retrieve.
  function getReleaseHashForPackage(string name, uint releaseIdx)
    public
    view
    returns (bytes32)
  {
    bytes32 nameHash = packageDb.hashName(name);
    return releaseDb.getReleaseHashForNameHash(nameHash, releaseIdx);
  }

  /// @dev Returns an array of all release hashes for the named package.
  /// @param name Package name
  function getAllPackageReleaseHashes(string name)
    public
    view
    returns (bytes32[])
  {
    uint numReleases;
    (,,numReleases,) = getPackageData(name);
    return getPackageReleaseHashes(name, 0, numReleases);
  }

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
    returns (bytes32[])
  {
    bytes32 nameHash = packageDb.hashName(name);
    bytes32[] memory releaseHashes = new bytes32[](numReleases);

    for (uint i = offset; i < offset + numReleases; i++) {
      releaseHashes[i] = releaseDb.getReleaseHashForNameHash(nameHash, i);
    }

    return releaseHashes;
  }

  function getNumReleases()
    public
    view
    returns (uint)
  {
    return releaseDb.getNumReleases();
  }

  /// @dev Returns an array of all release hashes for the named package.
  function getAllReleaseHashes()
    public
    view
    returns (bytes32[])
  {
    return getReleaseHashes(0, getNumReleases());
  }

  /// @dev Returns a slice of the array of all release hashes for the named package.
  /// @param offset The starting index for the slice.
  /// @param numReleases The length of the slice
  function getReleaseHashes(uint offset, uint numReleases)
    public
    view
    returns (bytes32[])
  {
    bytes32[] memory releaseHashes = new bytes32[](numReleases);

    for (uint i = offset; i < offset + numReleases; i++) {
      releaseHashes[i] = releaseDb.getReleaseHash(i);
    }

    return releaseHashes;
  }

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
    returns (string)
  {
    bytes32 versionHash = releaseDb.hashVersion(major, minor, patch, preRelease, build);
    bytes32 releaseHash = releaseDb.hashRelease(packageDb.hashName(name), versionHash);
    return getReleaseManifestURI(releaseHash);
  }


  //
  // +----------------+
  // |  Internal API  |
  // +----------------+
  //
  /// @dev Returns boolean whether the provided address is the package owner
  /// @param name The name of the package
  /// @param _address The address to check
  function isPackageOwner(string name, address _address)
    internal
    view
    returns (bool)
  {
    address packageOwner;
    (packageOwner,,,) = getPackageData(name);
    return (packageOwner != _address);
  }

  /// @dev Retrieves the name for the given name hash.
  /// @param nameHash The name hash to lookup the name for.
  function getPackageName(bytes32 nameHash)
    internal
    view
    returns (string)
  {
    return PackageDB(packageDb).getPackageName(nameHash);
  }

  /// @dev Retrieves the release manifest URI from the package db.
  /// @param releaseHash The release hash to retrieve the URI from.
  function getReleaseManifestURI(bytes32 releaseHash)
    internal
    view
    returns (string)
  {
    return ReleaseDB(releaseDb).getManifestURI(releaseHash);
  }

  /// @dev Retrieves the pre-release string from the package db.
  /// @param releaseHash The release hash to retrieve the string from.
  function getPreRelease(bytes32 releaseHash)
    internal
    view
    returns (string)
  {
    return ReleaseDB(releaseDb).getPreRelease(releaseHash);
  }

  /// @dev Retrieves the build string from the package db.
  /// @param releaseHash The release hash to retrieve the string from.
  function getBuild(bytes32 releaseHash)
    internal
    view
    returns (string)
  {
    return ReleaseDB(releaseDb).getBuild(releaseHash);
  }
}
