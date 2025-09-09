from enum import Enum
from typing import Literal


class ImageMediaSourceRefType(str, Enum):
    NEWSPAPER = "newspaper"

    def __str__(self) -> str:
        return str(self.value)


ImageMediaSourceRefTypeLiteral = Literal["newspaper",]
