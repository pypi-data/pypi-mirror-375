from typing import Any, List

from ausikor_common.utils.pagination.pagination_model import PaginationModel


class PaginationSchema:
    def __init__(self, items: List[Any], total: int, limit: int = None, offset: int = 0):
        self.page_model = PaginationModel()
        self.items = items
        self.total = total
        self.limit = limit or self.page_model.default_page_size
        self.offset = offset

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "limit": self.limit,
            "offset": self.offset,
            "items": self.items,
            "page": self.current_page,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev
        }

    @property
    def current_page(self) -> int:
        """현재 페이지 번호 (1부터 시작)"""
        return (self.offset // self.limit) + 1

    @property
    def total_pages(self) -> int:
        """전체 페이지 수"""
        return (self.total + self.limit - 1) // self.limit

    @property
    def has_next(self) -> bool:
        """다음 페이지 존재 여부"""
        return self.current_page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """이전 페이지 존재 여부"""
        return self.current_page > 1