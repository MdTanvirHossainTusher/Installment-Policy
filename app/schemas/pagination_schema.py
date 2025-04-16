from pydantic import BaseModel
from typing import Generic, List, Optional, TypeVar
from fastapi import Query

T = TypeVar('T')

class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(10, ge=1, le=100, description="Items per page"),
        sort_by: Optional[str] = Query(None, description="Sort field"),
        sort_dir: Optional[str] = Query(None, description="Sort direction (asc or desc)")
    ):
        self.page = page
        self.size = size
        self.sort_by = sort_by
        self.sort_dir = sort_dir


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int 
    size: int
    pages: int 
    has_next: bool
    has_previous: bool

    class Config:
        arbitrary_types_allowed = True