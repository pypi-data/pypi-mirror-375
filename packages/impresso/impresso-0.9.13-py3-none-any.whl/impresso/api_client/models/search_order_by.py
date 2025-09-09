from enum import Enum
from typing import Literal


class SearchOrderBy(str, Enum):
    DATE = "date"
    ID = "id"
    RELEVANCE = "relevance"
    VALUE_0 = "-date"
    VALUE_2 = "-relevance"
    VALUE_5 = "-id"

    def __str__(self) -> str:
        return str(self.value)


SearchOrderByLiteral = Literal[
    "date",
    "id",
    "relevance",
    "-date",
    "-relevance",
    "-id",
]
