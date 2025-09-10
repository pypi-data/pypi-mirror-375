# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Generic, TypeVar, Optional
from typing_extensions import override

from ._models import BaseModel
from ._base_client import BasePage, PageInfo, BaseSyncPage, BaseAsyncPage

__all__ = ["CursorPageMeta", "CursorPageCursors", "SyncCursorPage", "AsyncCursorPage"]

_T = TypeVar("_T")


class CursorPageCursors(BaseModel):
    next: Optional[str] = None


class CursorPageMeta(BaseModel):
    cursors: Optional[CursorPageCursors] = None


class SyncCursorPage(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    data: List[_T]
    meta: Optional[CursorPageMeta] = None

    @override
    def _get_page_items(self) -> List[_T]:
        data = self.data
        if not data:
            return []
        return data

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next = None
        if self.meta is not None:
            if self.meta.cursors is not None:
                if self.meta.cursors.next is not None:
                    next = self.meta.cursors.next
        if not next:
            return None

        return PageInfo(params={"after": next})


class AsyncCursorPage(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    data: List[_T]
    meta: Optional[CursorPageMeta] = None

    @override
    def _get_page_items(self) -> List[_T]:
        data = self.data
        if not data:
            return []
        return data

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next = None
        if self.meta is not None:
            if self.meta.cursors is not None:
                if self.meta.cursors.next is not None:
                    next = self.meta.cursors.next
        if not next:
            return None

        return PageInfo(params={"after": next})
