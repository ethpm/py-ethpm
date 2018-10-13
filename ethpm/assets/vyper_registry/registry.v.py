# todo
# delete pkgs

# Events
Release: event({_package: indexed(bytes32), _version: bytes32, _uri: bytes32})

owner: public(address)

# Package Data: (package_id => value)
packages: public(
    {
        exists: bool,
        createdAt: timestamp,
        updatedAt: timestamp,
        name: bytes32,
        releaseCount: int128,
    }[bytes32]
)

#  Release Data: (release_id => value)
releases: public(
    {
        exists: bool,
        createdAt: timestamp,
        packageId: bytes32,
        version: bytes32,
        uri: bytes32,
    }[bytes32]
)


# package_id#release_count => release_id
packageReleaseIndex: bytes32[bytes32]
# Total number of packages in registry
packageCount: public(int128)
# Total number of releases in registry
releaseCount: public(int128)
# Total package number (int128) => package_id (bytes32)
packageIds: bytes32[int128]
# Total release number (int128) => release_id (bytes32)
releaseIds: bytes32[int128]

EMPTY_BYTES: bytes32


@public
def __init__():
    self.owner = msg.sender


@public
def transferOwner(newOwner: address):
    """
    Change ownership of contract.
    """
    assert self.owner == msg.sender
    self.owner = newOwner


@public
def getReleaseId(packageName: bytes32, version: bytes32) -> bytes32:
    """
    Return the `release_id` associated with a given package name and release version.
    """
    releaseConcat: bytes[64] = concat(packageName, version)
    releaseId: bytes32 = sha3(releaseConcat)
    assert self.releases[releaseId].exists
    return releaseId


@public
def generateReleaseId(packageName: bytes32, version: bytes32) -> bytes32:
    releaseConcat: bytes[64] = concat(packageName, version)
    releaseId: bytes32 = sha3(releaseConcat)
    return releaseId


@public
def getPackageName(packageId: bytes32) -> bytes32:
    assert self.packages[packageId].exists
    return self.packages[packageId].name


@public
def getPackageData(packageName: bytes32) -> (bytes32, bytes32, int128):
    packageId: bytes32 = sha3(packageName)
    assert self.packages[packageId].exists
    return (
        self.packages[packageId].name,
        packageId,
        self.packages[packageId].releaseCount,
    )


@public
def getAllPackageIds(
    offset: uint256, length: uint256
) -> (bytes32, bytes32, bytes32, bytes32, bytes32):
    offset_int: int128 = convert(offset, "int128")
    length_int: int128 = convert(length, "int128")
    assert length_int == 5
    assert offset_int <= self.packageCount
    ids: bytes32[5]
    for idx in range(offset_int, offset_int + 4):
        if idx <= self.packageCount:
            packageId: bytes32 = self.packageIds[idx]
            ids[(idx - offset_int)] = packageId
        else:
            ids[(idx - offset_int)] = self.EMPTY_BYTES
    return (ids[0], ids[1], ids[2], ids[3], ids[4])


@private
def generatePackageReleaseId(packageId: bytes32, count: int128) -> bytes32:
    """
    Create the package_release_id associated with a given package_id and a release count.
    """
    countBytes: bytes32 = convert(count, "bytes32")
    packageReleaseTag: bytes[64] = concat(packageId, countBytes)
    packageReleaseId: bytes32 = sha3(packageReleaseTag)
    return packageReleaseId


@public
def getAllReleaseIds(
    packageName: bytes32, offset: uint256, length: uint256
) -> (bytes32, bytes32, bytes32, bytes32, bytes32):
    offset_int: int128 = convert(offset, "int128")
    length_int: int128 = convert(length, "int128")
    assert length_int == 5
    packageId: bytes32 = sha3(packageName)
    assert self.packages[packageId].exists
    assert offset_int <= self.packages[packageId].releaseCount
    ids: bytes32[5]
    for idx in range(offset_int, offset_int + 4):
        if idx <= self.packages[packageId].releaseCount:
            packageReleaseId: bytes32 = self.generatePackageReleaseId(
                packageId, (idx + 1)
            )
            releaseId: bytes32 = self.packageReleaseIndex[packageReleaseId]
            ids[(idx - offset_int)] = releaseId
        else:
            ids[(idx - offset_int)] = self.EMPTY_BYTES
    return (ids[0], ids[1], ids[2], ids[3], ids[4])


@public
def getReleaseData(releaseId: bytes32) -> (bytes32, bytes32, bytes32):
    assert self.releases[releaseId].exists
    packageId: bytes32 = self.releases[releaseId].packageId
    return (
        self.packages[packageId].name,
        self.releases[releaseId].version,
        self.releases[releaseId].uri,
    )


@private
def cutRelease(
    releaseId: bytes32,
    packageId: bytes32,
    version: bytes32,
    uri: bytes32,
    name: bytes32,
):
    self.releases[releaseId] = {
        exists: True,
        createdAt: block.timestamp,
        packageId: packageId,
        version: version,
        uri: uri,
    }
    self.packages[packageId].releaseCount += 1
    self.releaseIds[self.releaseCount] = releaseId
    self.releaseCount += 1
    packageReleaseId: bytes32 = self.generatePackageReleaseId(
        packageId, self.packages[packageId].releaseCount
    )
    self.packageReleaseIndex[packageReleaseId] = releaseId
    log.Release(name, version, uri)


@public
def release(name: bytes32, version: bytes32, uri: bytes32) -> bytes32:
    """
    Return a relase_id after publishing a release.
    """
    assert uri != self.EMPTY_BYTES
    assert name != self.EMPTY_BYTES
    assert version != self.EMPTY_BYTES
    assert self.owner == msg.sender

    packageId: bytes32 = sha3(name)
    releaseId: bytes32 = self.generateReleaseId(name, version)

    if self.packages[packageId].exists == True:
        self.packages[packageId] = {
            exists: True,
            createdAt: self.packages[packageId].createdAt,
            updatedAt: block.timestamp,
            name: name,
            releaseCount: self.packages[packageId].releaseCount,
        }
        assert self.releases[releaseId].exists == False
        self.cutRelease(releaseId, packageId, version, uri, name)
        return releaseId
    else:
        self.packages[packageId] = {
            exists: True,
            createdAt: block.timestamp,
            updatedAt: block.timestamp,
            name: name,
            releaseCount: 0,
        }
        self.packageIds[self.packageCount] = packageId
        self.packageCount += 1
        self.cutRelease(releaseId, packageId, version, uri, name)
        return releaseId
