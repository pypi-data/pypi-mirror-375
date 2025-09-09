import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.image_media_source_ref import ImageMediaSourceRef


T = TypeVar("T", bound="Image")


@_attrs_define
class Image:
    """An image from a content item

    Attributes:
        uid (str): The unique identifier of the image
        issue_uid (str): The unique identifier of the issue that the image belongs to.
        preview_url (str): The URL of the image preview
        media_source_ref (ImageMediaSourceRef): The media source of the image
        date (datetime.date): The date of the image or the date of the issue that the image belongs to.
        caption (Union[Unset, str]): Image caption
        content_item_uid (Union[Unset, str]): The unique identifier of the content item that the image belongs to.
        page_numbers (Union[Unset, List[int]]): The page numbers of the issue that the image belongs to.
    """

    uid: str
    issue_uid: str
    preview_url: str
    media_source_ref: "ImageMediaSourceRef"
    date: datetime.date
    caption: Union[Unset, str] = UNSET
    content_item_uid: Union[Unset, str] = UNSET
    page_numbers: Union[Unset, List[int]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid

        issue_uid = self.issue_uid

        preview_url = self.preview_url

        media_source_ref = self.media_source_ref.to_dict()

        date = self.date.isoformat()

        caption = self.caption

        content_item_uid = self.content_item_uid

        page_numbers: Union[Unset, List[int]] = UNSET
        if not isinstance(self.page_numbers, Unset):
            page_numbers = self.page_numbers

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "uid": uid,
                "issueUid": issue_uid,
                "previewUrl": preview_url,
                "mediaSourceRef": media_source_ref,
                "date": date,
            }
        )
        if caption is not UNSET:
            field_dict["caption"] = caption
        if content_item_uid is not UNSET:
            field_dict["contentItemUid"] = content_item_uid
        if page_numbers is not UNSET:
            field_dict["pageNumbers"] = page_numbers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.image_media_source_ref import ImageMediaSourceRef

        d = src_dict.copy()
        uid = d.pop("uid")

        issue_uid = d.pop("issueUid")

        preview_url = d.pop("previewUrl")

        media_source_ref = ImageMediaSourceRef.from_dict(d.pop("mediaSourceRef"))

        date = isoparse(d.pop("date")).date()

        caption = d.pop("caption", UNSET)

        content_item_uid = d.pop("contentItemUid", UNSET)

        page_numbers = cast(List[int], d.pop("pageNumbers", UNSET))

        image = cls(
            uid=uid,
            issue_uid=issue_uid,
            preview_url=preview_url,
            media_source_ref=media_source_ref,
            date=date,
            caption=caption,
            content_item_uid=content_item_uid,
            page_numbers=page_numbers,
        )

        return image
