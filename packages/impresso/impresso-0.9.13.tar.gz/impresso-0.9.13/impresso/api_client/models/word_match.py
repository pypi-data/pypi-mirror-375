from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="WordMatch")


@_attrs_define
class WordMatch:
    """Represents a word match result from word embeddings similarity search

    Attributes:
        id (str): Unique identifier for the word
        language_code (str): The language code of the word
        word (str): The word
    """

    id: str
    language_code: str
    word: str

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        language_code = self.language_code

        word = self.word

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "languageCode": language_code,
                "word": word,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        language_code = d.pop("languageCode")

        word = d.pop("word")

        word_match = cls(
            id=id,
            language_code=language_code,
            word=word,
        )

        return word_match
