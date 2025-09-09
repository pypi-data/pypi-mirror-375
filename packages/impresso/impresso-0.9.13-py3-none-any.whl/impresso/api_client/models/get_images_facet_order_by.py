from enum import Enum
from typing import Literal


class GetImagesFacetOrderBy(str, Enum):
    COUNT = "count"
    VALUE = "value"
    VALUE_0 = "-count"
    VALUE_2 = "-value"

    def __str__(self) -> str:
        return str(self.value)


GetImagesFacetOrderByLiteral = Literal[
    "count",
    "value",
    "-count",
    "-value",
]
