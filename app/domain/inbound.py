from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class Inbound:
    id: int
    remark: str
    protocol: str
    port: int
    raw: dict[str, Any]