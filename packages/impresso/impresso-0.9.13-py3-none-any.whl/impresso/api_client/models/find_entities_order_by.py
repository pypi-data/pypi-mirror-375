from enum import Enum
from typing import Literal


class FindEntitiesOrderBy(str, Enum):
    COUNT = "count"
    COUNT_MENTIONS = "count-mentions"
    NAME = "name"
    RELEVANCE = "relevance"
    VALUE_1 = "-relevance"
    VALUE_3 = "-name"
    VALUE_5 = "-count"
    VALUE_7 = "-count-mentions"

    def __str__(self) -> str:
        return str(self.value)


FindEntitiesOrderByLiteral = Literal[
    "count",
    "count-mentions",
    "name",
    "relevance",
    "-relevance",
    "-name",
    "-count",
    "-count-mentions",
]
