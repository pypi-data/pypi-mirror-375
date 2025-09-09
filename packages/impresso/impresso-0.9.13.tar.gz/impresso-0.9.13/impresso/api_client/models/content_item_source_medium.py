from enum import Enum
from typing import Literal


class ContentItemSourceMedium(str, Enum):
    AUDIO = "audio"
    PRINT = "print"
    TYPESCRIPT = "typescript"

    def __str__(self) -> str:
        return str(self.value)


ContentItemSourceMediumLiteral = Literal[
    "audio",
    "print",
    "typescript",
]
