from enum import Enum
from typing import Literal


class FindMediaSourcesOrderBy(str, Enum):
    COUNTISSUES = "countIssues"
    FIRSTISSUE = "firstIssue"
    LASTISSUE = "lastIssue"
    NAME = "name"
    VALUE_1 = "-name"
    VALUE_3 = "-firstIssue"
    VALUE_5 = "-lastIssue"
    VALUE_7 = "-countIssues"

    def __str__(self) -> str:
        return str(self.value)


FindMediaSourcesOrderByLiteral = Literal[
    "countIssues",
    "firstIssue",
    "lastIssue",
    "name",
    "-name",
    "-firstIssue",
    "-lastIssue",
    "-countIssues",
]
