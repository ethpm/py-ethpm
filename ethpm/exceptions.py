class InsufficientAssetsError(Exception):
    """
    Error to signal a Manifest or Package does not
    contain the required assets to do something.
    """


class UriNotSupportedError(Exception):
    """
    Error to signal a URI scheme is not supported.
    """


class ValidationError(Exception):
    """
    Error to signal something does not pass a validation check.
    """
    pass
