class PyEVMError(Exception):
    """
    Base error class for all py-evm errors.
    """
    pass


class ValidationError(PyEVMError):
    """
    Error to signal something does not pass a validation check.
    """
    pass
