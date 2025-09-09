from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateCollectableItemsRequest")


@_attrs_define
class UpdateCollectableItemsRequest:
    """Request to update collectible items in a collection

    Attributes:
        add (Union[Unset, List[str]]): IDs of the items to add to the collection
        remove (Union[Unset, List[str]]): IDs of the items to remove from the collection
    """

    add: Union[Unset, List[str]] = UNSET
    remove: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        add: Union[Unset, List[str]] = UNSET
        if not isinstance(self.add, Unset):
            add = self.add

        remove: Union[Unset, List[str]] = UNSET
        if not isinstance(self.remove, Unset):
            remove = self.remove

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if add is not UNSET:
            field_dict["add"] = add
        if remove is not UNSET:
            field_dict["remove"] = remove

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        add = cast(List[str], d.pop("add", UNSET))

        remove = cast(List[str], d.pop("remove", UNSET))

        update_collectable_items_request = cls(
            add=add,
            remove=remove,
        )

        update_collectable_items_request.additional_properties = d
        return update_collectable_items_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
