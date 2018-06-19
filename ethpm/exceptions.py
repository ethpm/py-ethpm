class InsufficientAssetsError(Exception):
    """
    Error to signal a Manifest or Package does not
    contain the required assets to do something.
    """


class ValidationError(Exception):
    """
    Error to signal something does not pass a validation check.
    """
    pass
