from abc import ABC, abstractmethod

from ethpm.utils.ipfs import extract_ipfs_path_from_uri


# generic backend that all URI backends come from
class BaseURIBackend(ABC):
    def can_handle_uri(self, uri) -> bool:
        """
        Returns bool for whether this backend class can handle the given URI.
        """
        pass

    def fetch_uri_contents(uri):
        """
        Fetch the contents stored at a URI.
        """
        pass


# glue code in the core logic that fetches URIS
def get_backends_for_uri(backends, uri):
    return tuple(backend for backend in backends if backend.can_handle_uri(uri))


# and then some code to loop over the *good* backends and return the fetched contents
# maybe an exception that the backends can raise if for some reason they find that can't handle it
def get_uri_contents(): 
    for backend in good_backends:
        try:
            contents = backend.fetch_uri_contents(uri)
        except CannotHandleURI: # custom exception
            continue
        else:
            return contents
    else:
        raise SomethingError("No backends were able to fetch the URI contents")
