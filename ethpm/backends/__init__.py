from .http import GithubOverHTTPSBackend
from .ipfs import InfuraIPFSBackend, DummyIPFSBackend, LocalIPFSBackend
from .registry import RegistryURIBackend

ALL_URI_BACKENDS = [
    InfuraIPFSBackend,
    DummyIPFSBackend,
    LocalIPFSBackend,
    GithubOverHTTPSBackend,
    RegistryURIBackend,
]
