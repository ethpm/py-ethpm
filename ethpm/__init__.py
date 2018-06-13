import sys
import warnings

from pathlib import Path

if sys.version_info.major < 3:
    warn_msg = ("Python 2 support will end during the first quarter of 2018"
                "Please upgrade to Python 3"
                "https://medium.com/@pipermerriam/dropping-python-2-support-d781e7b48160"
                )
    warnings.warn(warn_msg, DeprecationWarning)


BASE_DIR = Path('.')
ETHPM_SPEC_DIR = BASE_DIR.parent / 'ethpm-spec'
SPEC_DIR = ETHPM_SPEC_DIR / 'spec'  # type: Path
V2_PACKAGES = ETHPM_SPEC_DIR / 'examples'

from .package import Package  # noqa: F401
