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
    Raised when URI scheme does not conform to the registry URI scheme.
    """
    pass
