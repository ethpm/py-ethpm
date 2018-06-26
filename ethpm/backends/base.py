from abc import (
    ABC,
    abstractmethod,
)


class BaseURIBackend(ABC):
    """
    Generic backend that all URI backends are subclassed from.

    All subclasses must implement:
    can_handle_uri, fetch_uri_contents, base_uri
    """
    @abstractmethod
    def can_handle_uri(self, uri: str) -> bool:
        """
        Return a bool indicating whether this backend class can handle the given URI.
        """
        raise NotImplementedError("Must be implemented by subclass.")

    @abstractmethod
    def fetch_uri_contents(self, uri: str) -> bytes:
        """
        Fetch the contents stored at a URI.
        """
        raise NotImplementedError("Must be implemented by subclass.")

    @property
    @abstractmethod
    def base_uri(self) -> str:
        """
        Return the base URI unique to a particular scheme.
        """
        raise NotImplementedError("Must be implemented by subclass.")
