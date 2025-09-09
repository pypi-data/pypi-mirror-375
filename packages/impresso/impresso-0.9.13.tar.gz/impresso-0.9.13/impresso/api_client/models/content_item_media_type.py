from enum import Enum
from typing import Literal


class ContentItemMediaType(str, Enum):
    ENCYCLOPEDIA = "encyclopedia"
    MONOGRAPH = "monograph"
    NEWSPAPER = "newspaper"
    RADIO_BROADCAST = "radio_broadcast"
    RADIO_MAGAZINE = "radio_magazine"
    RADIO_SCHEDULE = "radio_schedule"

    def __str__(self) -> str:
        return str(self.value)


ContentItemMediaTypeLiteral = Literal[
    "encyclopedia",
    "monograph",
    "newspaper",
    "radio_broadcast",
    "radio_magazine",
    "radio_schedule",
]
