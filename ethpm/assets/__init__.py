import json
from typing import Any, Dict

from ethpm import ASSETS_DIR


def get_manifest(use_case: str, filename: str) -> Dict[str, Any]:
    with open(str(ASSETS_DIR / use_case / filename)) as f:
        return json.load(f)
