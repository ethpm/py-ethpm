class PyEthPMError(Exception):
    """
    Base class for all Py-EthPM errors.
    """

    pass


class InsufficientAssetsError(PyEthPMError):
    """
    Raised when a Manifest or Package does not
    contain the required assets to do something.
    """

    pass


class ValidationError(PyEthPMError):
    """
    Raised when something does not pass a validation check.
    """

    pass


class UriNotSupportedError(ValidationError):
    """
    Raised when URI scheme is invalid or not supported by the current backend.
    """

    pass


class FailureToFetchIPFSAssetsError(PyEthPMError):
    """
    Raised when an attempt to fetch a Package's assets via IPFS failed.
    """

    pass
