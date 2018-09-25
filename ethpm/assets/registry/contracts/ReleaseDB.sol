pragma solidity ^0.4.24;
pragma experimental "v0.5.0";

import {SemVersionLib} from "./SemVersionLib.sol";
import {IndexedOrderedSetLib} from "./IndexedOrderedSetLib.sol";
import {Authorized} from "./Authority.sol";


/// @title Database contract for a package index.
/// @author Tim Coulter <tim.coulter@consensys.net>, Piper Merriam <pipermerriam@gmail.com>
contract ReleaseDB is Authorized {
  using SemVersionLib for SemVersionLib.SemVersion;
  using IndexedOrderedSetLib for IndexedOrderedSetLib.IndexedOrderedSet;

  struct Release {
    bool exists;
    uint createdAt;
    uint updatedAt;
    bytes32 nameHash;
    bytes32 versionHash;
    string manifestURI;
  }

  // Release Data: (releaseHash => value)
  mapping (bytes32 => Release) _recordedReleases;
  IndexedOrderedSetLib.IndexedOrderedSet _allReleaseHashes;
  mapping (bytes32 => IndexedOrderedSetLib.IndexedOrderedSet) _releaseHashesByNameHash;

  // Version Data: (versionHash => value)
  mapping (bytes32 => SemVersionLib.SemVersion) _recordedVersions;
  mapping (bytes32 => bool) _versionExists;

  // Events
  event ReleaseCreate(bytes32 indexed releaseHash);
  event ReleaseUpdate(bytes32 indexed releaseHash);
  event ReleaseDelete(bytes32 indexed releaseHash, string reason);

  /*
   * Latest released version tracking for each branch of the release tree.
   */
  // (nameHash => releaseHash);
  mapping (bytes32 => bytes32) _latestMajor;

  // (nameHash => major => releaseHash);
  mapping (bytes32 => mapping(uint32 => bytes32)) _latestMinor;

  // (nameHash => major => minor => releaseHash);
  mapping (bytes32 => mapping (uint32 => mapping(uint32 => bytes32))) _latestPatch;

  // (nameHash => major => minor => patch => releaseHash);
  mapping (bytes32 => mapping (uint32 => mapping(uint32 => mapping (uint32 => bytes32)))) _latestPreRelease;

  /*
   *  Modifiers
   */
  modifier onlyIfVersionExists(bytes32 versionHash) {
    require(versionExists(versionHash), "escape:ReleaseDB:version-not-found");
    _;
  }

  modifier onlyIfReleaseExists(bytes32 releaseHash) {
    require(releaseExists(releaseHash), "escape:ReleaseDB:release-not-found");
    _;
  }

  //
  // +-------------+
  // |  Write API  |
  // +-------------+
  //

  /// @dev Creates or updates a release for a package.  Returns success.
  /// @param nameHash The name hash of the package.
  /// @param versionHash The version hash for the release version.
  /// @param manifestURI The URI for the release manifest for this release.
  function setRelease(
    bytes32 nameHash,
    bytes32 versionHash,
    string manifestURI
  )
    public
    auth
    returns (bool)
  {
    bytes32 releaseHash = hashRelease(nameHash, versionHash);

    Release storage release = _recordedReleases[releaseHash];

    // If this is a new version push it onto the array of version hashes for
    // this package.
    if (release.exists) {
      emit ReleaseUpdate(releaseHash);
    } else {
      // Populate the basic rlease data.
      release.exists = true;
      release.createdAt = block.timestamp; // solium-disable-line security/no-block-members
      release.nameHash = nameHash;
      release.versionHash = versionHash;

      // Push the release hash into the array of all release hashes.
      _allReleaseHashes.add(releaseHash);
      _releaseHashesByNameHash[nameHash].add(releaseHash);

      emit ReleaseCreate(releaseHash);
    }

    // Record the last time the release was updated.
    release.updatedAt = block.timestamp; // solium-disable-line security/no-block-members

    // Save the release manifest URI
    release.manifestURI = manifestURI;

    // Track latest released versions for each branch of the release tree.
    updateLatestTree(releaseHash);

    return true;
  }

  /// @dev Removes a release from a package.  Returns success.
  /// @param releaseHash The release hash to be removed
  /// @param reason Explanation for why the removal happened.
  function removeRelease(bytes32 releaseHash, string reason)
    public
    auth
    onlyIfReleaseExists(releaseHash)
    returns (bool)
  {
    bytes32 nameHash;
    bytes32 versionHash;
    uint32 major;
    uint32 minor;
    uint32 patch;

    (nameHash, versionHash,,) = getReleaseData(releaseHash);
    (major, minor, patch) = getMajorMinorPatch(versionHash);

    // In any branch of the release tree in which this version is the latest we
    // remove it.  This will leave the release tree for this package in an
    // invalid state.  The `updateLatestTree` function` provides a path to
    // recover from this state.  The naive approach would be to call it on all
    // release hashes in the array of remaining package release hashes which
    // will properly repopulate the release tree for this package.
    if (isLatestMajorTree(nameHash, versionHash)) {
      delete _latestMajor[nameHash];
    }
    if (isLatestMinorTree(nameHash, versionHash)) {
      delete _latestMinor[nameHash][major];
    }
    if (isLatestPatchTree(nameHash, versionHash)) {
      delete _latestPatch[nameHash][major][minor];
    }
    if (isLatestPreReleaseTree(nameHash, versionHash)) {
      delete _latestPreRelease[nameHash][major][minor][patch];
    }

    // Zero out the release data.
    delete _recordedReleases[releaseHash];

    // Remove the release hash from the list of all release hashes
    _allReleaseHashes.remove(releaseHash);
    _releaseHashesByNameHash[nameHash].remove(releaseHash);

    // Log the removal.
    emit ReleaseDelete(releaseHash, reason);

    return true;
  }

  /// @dev Updates each branch of the tree, replacing the current leaf node with this release hash if this release hash should be the new leaf.  Returns success.
  /// @param releaseHash The releaseHash to check.
  function updateLatestTree(bytes32 releaseHash)
    public
    auth
    returns (bool)
  {
    updateMajorTree(releaseHash);
    updateMinorTree(releaseHash);
    updatePatchTree(releaseHash);
    updatePreReleaseTree(releaseHash);
    return true;
  }

  /// @dev Adds the given version to the local version database.  Returns the versionHash for the provided version.
  /// @param major The major portion of the semver version string.
  /// @param minor The minor portion of the semver version string.
  /// @param patch The patch portion of the semver version string.
  /// @param preRelease The pre-release portion of the semver version string.  Use empty string if the version string has no pre-release portion.
  /// @param build The build portion of the semver version string.  Use empty string if the version string has no build portion.
  function setVersion(
    uint32 major,
    uint32 minor,
    uint32 patch,
    string preRelease,
    string build
  )
    public
    auth
    returns (bytes32)
  {
    bytes32 versionHash = hashVersion(major, minor, patch, preRelease, build);

    if (!_versionExists[versionHash]) {
      _recordedVersions[versionHash].init(major, minor, patch, preRelease, build);
      _versionExists[versionHash] = true;
    }
    return versionHash;
  }

  //
  // +------------+
  // |  Read API  |
  // +------------+
  //

  /// @dev Get the total number of releases
  function getNumReleases()
    public
    view
    returns (uint)
  {
    return _allReleaseHashes.size();
  }

  /// @dev Get the total number of releases
  /// @param idx The index of the release hash to retrieve.
  function getReleaseHash(uint idx)
    public
    view
    returns (bytes32)
  {
    return _allReleaseHashes.get(idx);
  }

  /// @dev Get the total number of releases
  /// @param nameHash the name hash to lookup.
  function getNumReleasesForNameHash(bytes32 nameHash)
    public
    view
    returns (uint)
  {
    return _releaseHashesByNameHash[nameHash].size();
  }

  /// @dev Get the total number of releases
  /// @param nameHash the name hash to lookup.
  /// @param idx The index of the release hash to retrieve.
  function getReleaseHashForNameHash(bytes32 nameHash, uint idx)
    public
    view
    returns (bytes32)
  {
    return _releaseHashesByNameHash[nameHash].get(idx);
  }

  /// @dev Query the existence of a release at the provided version for a package.  Returns boolean indicating whether such a release exists.
  /// @param releaseHash The release hash to query.
  function releaseExists(bytes32 releaseHash)
    public
    view
    returns (bool)
  {
    return _recordedReleases[releaseHash].exists;
  }

  /// @dev Query the existence of the provided version in the recorded versions.  Returns boolean indicating whether such a version exists.
  /// @param versionHash the version hash to check.
  function versionExists(bytes32 versionHash)
    public
    view
    returns (bool)
  {
    return _versionExists[versionHash];
  }

  /// @dev Returns the releaseHash at the given index for a package.
  /// @param releaseHash The release hash.
  function getReleaseData(bytes32 releaseHash)
    public
    view
    onlyIfReleaseExists(releaseHash)
    returns (
      bytes32 nameHash,
      bytes32 versionHash,
      uint createdAt,
      uint updatedAt
    )
  {
    Release storage release = _recordedReleases[releaseHash];
    return (release.nameHash, release.versionHash, release.createdAt, release.updatedAt);
  }

  /// @dev Returns a 3-tuple of the major, minor, and patch components from the version of the given release hash.
  /// @param versionHash the version hash
  function getMajorMinorPatch(bytes32 versionHash)
    public
    view
    onlyIfVersionExists(versionHash)
    returns (uint32, uint32, uint32)
  {
    SemVersionLib.SemVersion storage version = _recordedVersions[versionHash];
    return (version.major, version.minor, version.patch);
  }

  /// @dev Returns the pre-release string from the version of the given release hash.
  /// @param releaseHash Release hash
  function getPreRelease(bytes32 releaseHash)
    public
    view
    onlyIfReleaseExists(releaseHash)
    returns (string)
  {
    return _recordedVersions[_recordedReleases[releaseHash].versionHash].preRelease;
  }

  /// @dev Returns the build string from the version of the given release hash.
  /// @param releaseHash Release hash
  function getBuild(bytes32 releaseHash)
    public
    view
    onlyIfReleaseExists(releaseHash)
    returns (string)
  {
    return _recordedVersions[_recordedReleases[releaseHash].versionHash].build;
  }

  /// @dev Returns the URI of the release manifest for the given release hash.
  /// @param releaseHash Release hash
  function getManifestURI(bytes32 releaseHash)
    public
    view
    onlyIfReleaseExists(releaseHash)
    returns (string)
  {
    return _recordedReleases[releaseHash].manifestURI;
  }

  /*
   *  Hash Functions
   */
  /// @dev Returns version hash for the given semver version.
  /// @param major The major portion of the semver version string.
  /// @param minor The minor portion of the semver version string.
  /// @param patch The patch portion of the semver version string.
  /// @param preRelease The pre-release portion of the semver version string.  Use empty string if the version string has no pre-release portion.
  /// @param build The build portion of the semver version string.  Use empty string if the version string has no build portion.
  function hashVersion(
    uint32 major,
    uint32 minor,
    uint32 patch,
    string preRelease,
    string build
  )
    public
    pure
    returns (bytes32)
  {
    return keccak256(abi.encodePacked(major, minor, patch, preRelease, build));
  }

  /// @dev Returns release hash for the given release
  /// @param nameHash The name hash of the package name.
  /// @param versionHash The version hash for the release version.
  function hashRelease(bytes32 nameHash, bytes32 versionHash)
    public
    pure
    returns (bytes32)
  {
    return keccak256(abi.encodePacked(nameHash, versionHash));
  }

  /*
   *  Latest version querying API
   */

  /// @dev Returns the release hash of the latest release in the major branch of the package release tree.
  /// @param nameHash The nameHash of the package
  function getLatestMajorTree(bytes32 nameHash)
    public
    view
    returns (bytes32)
  {
    return _latestMajor[nameHash];
  }

  /// @dev Returns the release hash of the latest release in the minor branch of the package release tree.
  /// @param nameHash The nameHash of the package
  /// @param major The branch of the major portion of the release tree to check.
  function getLatestMinorTree(bytes32 nameHash, uint32 major)
    public
    view
    returns (bytes32)
  {
    return _latestMinor[nameHash][major];
  }

  /// @dev Returns the release hash of the latest release in the patch branch of the package release tree.
  /// @param nameHash The nameHash of the package
  /// @param major The branch of the major portion of the release tree to check.
  /// @param minor The branch of the minor portion of the release tree to check.
  function getLatestPatchTree(
    bytes32 nameHash,
    uint32 major,
    uint32 minor
  )
    public
    view
    returns (bytes32)
  {
    return _latestPatch[nameHash][major][minor];
  }

  /// @dev Returns the release hash of the latest release in the pre-release branch of the package release tree.
  /// @param nameHash The nameHash of the package
  /// @param major The branch of the major portion of the release tree to check.
  /// @param minor The branch of the minor portion of the release tree to check.
  /// @param patch The branch of the patch portion of the release tree to check.
  function getLatestPreReleaseTree(
    bytes32 nameHash,
    uint32 major,
    uint32 minor,
    uint32 patch
  )
    public
    view
    returns (bytes32)
  {
    return _latestPreRelease[nameHash][major][minor][patch];
  }

  /// @dev Returns boolean indicating whethe the given version hash is the latest version in the major branch of the release tree.
  /// @param nameHash The nameHash of the package to check against.
  /// @param versionHash The versionHash of the version to check.
  function isLatestMajorTree(bytes32 nameHash, bytes32 versionHash)
    public
    view
    onlyIfVersionExists(versionHash)
    returns (bool)
  {
    SemVersionLib.SemVersion storage version = _recordedVersions[versionHash];

    SemVersionLib.SemVersion storage latestMajor = // solium-disable-line operator-whitespace
      _recordedVersions[
        _recordedReleases[
          getLatestMajorTree(nameHash)
        ].versionHash
      ];

    return version.isGreaterOrEqual(latestMajor);
  }

  /// @dev Returns boolean indicating whethe the given version hash is the latest version in the minor branch of the release tree.
  /// @param nameHash The nameHash of the package to check against.
  /// @param versionHash The versionHash of the version to check.
  function isLatestMinorTree(bytes32 nameHash, bytes32 versionHash)
    public
    view
    onlyIfVersionExists(versionHash)
    returns (bool)
  {
    SemVersionLib.SemVersion storage version = _recordedVersions[versionHash];

    SemVersionLib.SemVersion storage latestMinor = // solium-disable-line operator-whitespace
      _recordedVersions[
        _recordedReleases[
          getLatestMinorTree(nameHash, version.major)
        ].versionHash
      ];

    return version.isGreaterOrEqual(latestMinor);
  }

  /// @dev Returns boolean indicating whethe the given version hash is the latest version in the patch branch of the release tree.
  /// @param nameHash The nameHash of the package to check against.
  /// @param versionHash The versionHash of the version to check.
  function isLatestPatchTree(bytes32 nameHash, bytes32 versionHash)
    public
    view
    onlyIfVersionExists(versionHash)
    returns (bool)
  {
    SemVersionLib.SemVersion storage version = _recordedVersions[versionHash];

    SemVersionLib.SemVersion storage latestPatch = // solium-disable-line operator-whitespace
      _recordedVersions[
        _recordedReleases[
          getLatestPatchTree(
            nameHash,
            version.major,
            version.minor
          )
        ].versionHash
      ];

    return version.isGreaterOrEqual(latestPatch);
  }

  /// @dev Returns boolean indicating whethe the given version hash is the latest version in the pre-release branch of the release tree.
  /// @param nameHash The nameHash of the package to check against.
  /// @param versionHash The versionHash of the version to check.
  function isLatestPreReleaseTree(bytes32 nameHash, bytes32 versionHash)
    public
    view
    onlyIfVersionExists(versionHash)
    returns (bool)
  {
    SemVersionLib.SemVersion storage version = _recordedVersions[versionHash];

    SemVersionLib.SemVersion storage latestPreRelease = // solium-disable-line operator-whitespace
      _recordedVersions[
        _recordedReleases[
          getLatestPreReleaseTree(
            nameHash,
            version.major,
            version.minor,
            version.patch
          )
        ].versionHash
      ];

    return version.isGreaterOrEqual(latestPreRelease);
  }

  //
  // +----------------+
  // |  Internal API  |
  // +----------------+
  //

  /*
   *  Tracking of latest releases for each branch of the release tree.
   */

  /// @dev Sets the given release as the new leaf of the major branch of the release tree if it is greater or equal to the current leaf.
  /// @param releaseHash The release hash of the release to check.
  function updateMajorTree(bytes32 releaseHash)
    internal
    onlyIfReleaseExists(releaseHash)
    returns (bool)
  {
    bytes32 nameHash;
    bytes32 versionHash;

    (nameHash, versionHash,,) = getReleaseData(releaseHash);

    if (isLatestMajorTree(nameHash, versionHash)) {
      _latestMajor[nameHash] = releaseHash;
      return true;
    } else {
      return false;
    }
  }

  /// @dev Sets the given release as the new leaf of the minor branch of the release tree if it is greater or equal to the current leaf.
  /// @param releaseHash The release hash of the release to check.
  function updateMinorTree(bytes32 releaseHash) internal returns (bool) {
    bytes32 nameHash;
    bytes32 versionHash;

    (nameHash, versionHash,,) = getReleaseData(releaseHash);

    if (isLatestMinorTree(nameHash, versionHash)) {
      uint32 major;
      (major,,) = getMajorMinorPatch(versionHash);
      _latestMinor[nameHash][major] = releaseHash;
      return true;
    } else {
      return false;
    }
  }

  /// @dev Sets the given release as the new leaf of the patch branch of the release tree if it is greater or equal to the current leaf.
  /// @param releaseHash The release hash of the release to check.
  function updatePatchTree(bytes32 releaseHash) internal returns (bool) {
    bytes32 nameHash;
    bytes32 versionHash;

    (nameHash, versionHash,,) = getReleaseData(releaseHash);

    if (isLatestPatchTree(nameHash, versionHash)) {
      uint32 major;
      uint32 minor;
      (major, minor,) = getMajorMinorPatch(versionHash);
      _latestPatch[nameHash][major][minor] = releaseHash;
      return true;
    } else {
      return false;
    }
  }

  /// @dev Sets the given release as the new leaf of the pre-release branch of the release tree if it is greater or equal to the current leaf.
  /// @param releaseHash The release hash of the release to check.
  function updatePreReleaseTree(bytes32 releaseHash) internal returns (bool) {
    bytes32 nameHash;
    bytes32 versionHash;

    (nameHash, versionHash,,) = getReleaseData(releaseHash);

    if (isLatestPreReleaseTree(nameHash, versionHash)) {
      uint32 major;
      uint32 minor;
      uint32 patch;

      (major, minor, patch) = getMajorMinorPatch(versionHash);
      _latestPreRelease[nameHash][major][minor][patch] = releaseHash;
      return true;
    } else {
      return false;
    }
  }
}
