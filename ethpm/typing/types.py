from typing import Any, Dict, NewType

Address = NewType("Address", bytes)
ContractName = NewType("ContractName", str)
Manifest = NewType("Manifest", Dict[str, Any])
URI = NewType("URI", str)
