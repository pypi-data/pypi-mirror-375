from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..models.image_media_source_ref_type import ImageMediaSourceRefType
from ..types import UNSET, Unset

T = TypeVar("T", bound="ImageMediaSourceRef")


@_attrs_define
class ImageMediaSourceRef:
    """The media source of the image

    Attributes:
        uid (str): The unique identifier of the media source
        name (str): The name of the media source
        type (Union[Unset, ImageMediaSourceRefType]): The type of the media source
    """

    uid: str
    name: str
    type: Union[Unset, ImageMediaSourceRefType] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid

        name = self.name

        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "uid": uid,
                "name": name,
            }
        )
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        uid = d.pop("uid")

        name = d.pop("name")

        _type = d.pop("type", UNSET)
        type: Union[Unset, ImageMediaSourceRefType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = ImageMediaSourceRefType(_type)

        image_media_source_ref = cls(
            uid=uid,
            name=name,
            type=type,
        )

        return image_media_source_ref
