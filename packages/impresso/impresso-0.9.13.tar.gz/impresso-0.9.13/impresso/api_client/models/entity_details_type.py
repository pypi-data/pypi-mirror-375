from enum import Enum
from typing import Literal


class EntityDetailsType(str, Enum):
    LOCATION = "location"
    NEWSAGENCY = "newsagency"
    ORGANISATION = "organisation"
    PERSON = "person"

    def __str__(self) -> str:
        return str(self.value)


EntityDetailsTypeLiteral = Literal[
    "location",
    "newsagency",
    "organisation",
    "person",
]
