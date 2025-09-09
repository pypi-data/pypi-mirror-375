from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="NamedEntity")


@_attrs_define
class NamedEntity:
    """An named entity (location, persion, etc) present in text.

    Attributes:
        uid (str): Unique identifier of the entity
        count (Union[Unset, float]): How many times it is mentioned in the text
    """

    uid: str
    count: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid

        count = self.count

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "uid": uid,
            }
        )
        if count is not UNSET:
            field_dict["count"] = count

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        uid = d.pop("uid")

        count = d.pop("count", UNSET)

        named_entity = cls(
            uid=uid,
            count=count,
        )

        return named_entity
