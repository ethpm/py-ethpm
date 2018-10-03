pragma solidity ^0.4.24;
pragma experimental "v0.5.0";


/// @title EIP 1319 Smart Contract Package Registry Interface
/// @author Piper Merriam <pipermerriam@gmail.com>, Christopher Gewecke <christophergewecke@gmail.com>
contract PackageRegistryInterface {

  //
  // +-------------+
  // |  Write API  |
  // +-------------+
  //

  /// @dev Creates a a new release for the named package.
  /// @notice Will create a new release the given package with the given release information.
  /// @param name Package name
  /// @param version Version string (ex: 1.0.0)
  /// @param manifestURI The URI for the release manifest for this release.
  function release(
    string name,
    string version,
    string manifestURI
  )
    public
    returns (bytes32 releaseId);

  //
  // +------------+
  // |  Read API  |
  // +------------+
  //

  /// @dev Returns the string name of the package associated with a package id
  /// @param packageId The package id to look up
  function getPackageName(bytes32 packageId)
    public
    view
    returns (string);

  /// @dev Returns a slice of the array of all package ids for the named package.
  /// @param offset The starting index for the slice.
  /// @param limit  The length of the slice
  function getAllPackageIds(uint offset, uint limit)
    public
    view
    returns (
      bytes32[] ids,
      uint _offset
    );

  /// @dev Returns a slice of the array of all release hashes for the named package.
  /// @param name Package name
  /// @param offset The starting index for the slice.
  /// @param limit  The length of the slice
  function getAllReleaseIds(string name, uint offset, uint limit)
    public
    view
    returns (
      bytes32[] ids,
      uint _offset
    );

  /// @dev Returns the package data for a release.
  /// @param releaseId Release id
  function getReleaseData(bytes32 releaseId)
    public
    view
    returns (
      string packageName,
      string version,
      string manifestURI
    );

  // @dev Returns release id that *would* be generated for a name and version pair on `release`.
  // @param name Package name
  // @param version Version string (ex: '1.0.0')
  function generateReleaseId(string name, string version)
    public
    view
    returns (bytes32);
}
