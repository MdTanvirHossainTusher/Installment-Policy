from typing import Optional

from pydantic import BaseModel, Field
from pydantic.v1 import root_validator

class CategoryBase(BaseModel):
    pass

class CategoryCreateRequest(CategoryBase):
    name: str = Field(..., min_length=2, description='Enter a category name')

    @root_validator
    def validate_name(cls, values):
        if values.get("name").strip() == "" or values.get("name") is None:
            raise ValueError("Category name can't be empty")
        return values

class CategoryUpdateRequest(CategoryCreateRequest):
    pass

class CategoryResponse(BaseModel):
    id: int
    name: str
