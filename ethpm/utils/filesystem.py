import json

from typing import (
    Dict,
    IO,
)


def load_package_data_from_file(file_obj: IO[str]) -> Dict[str, str]:
    """
    Utility function to load package objects
    from file objects passed to Package.from_file
    """
    try:
        package_data = json.load(file_obj)
    except json.JSONDecodeError as err:
        raise json.JSONDecodeError(
            "Failed to load package data. File is not a valid JSON document.",
            err.doc,
            err.pos,
        )

    return package_data
