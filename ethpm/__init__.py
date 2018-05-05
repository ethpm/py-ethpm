import os
import sys
import warnings

if sys.version_info.major < 3:
    warn_msg = ("Python 2 support will end during the first quarter of 2018"
                "Please upgrade to Python 3"
                "https://medium.com/@pipermerriam/dropping-python-2-support-d781e7b48160"
                )
    warnings.warn(warn_msg, DeprecationWarning)


BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR: str = os.path.join(BASE_DIR, 'assets')

from .package import Package  # noqa: F401
