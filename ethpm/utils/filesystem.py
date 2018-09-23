import json
from pathlib import Path
from typing import IO, Any, Dict


def load_json_from_file_path(path: Path) -> Dict[Any, Any]:
    with open(str(path)) as f:
        return json.load(f)


def load_manifest_from_file(file_obj: IO[str]) -> Dict[str, str]:
    """
    Utility function to load package objects
    from file objects passed to Package.from_file
    """
    try:
        manifest = json.load(file_obj)
    except json.JSONDecodeError as err:
        raise json.JSONDecodeError(
            "Failed to load package data. File is not a valid JSON document.",
            err.doc,
            err.pos,
        )

    return manifest
