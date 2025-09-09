from enum import Enum
from typing import Literal


class FindImagesOrderBy(str, Enum):
    DATE = "date"
    VALUE_1 = "-date"

    def __str__(self) -> str:
        return str(self.value)


FindImagesOrderByLiteral = Literal[
    "date",
    "-date",
]
