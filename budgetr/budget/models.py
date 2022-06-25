from datetime import datetime
from typing import Any

from pydantic import BaseModel, validator


class Transaction(BaseModel):
    title: str
    value: float
    category: str
    value_type: str
    id: int = None
    user_id: str = None
    created: Any = None

    @validator("value_type")
    def has_value_type(cls, v):
        if not v:
            raise ValueError("value_type must be income or expense")
        return v

    @validator("value")
    def has_value(cls, v):
        if not v:
            raise ValueError("value must be a number")
        return v

    @validator("category")
    def has_category(cls, v):
        if not v:
            raise ValueError("category must be a string")
        return v

    @validator("title")
    def has_title(cls, v):
        if not v:
            raise ValueError("title must be a string")
        return v

    @validator("created")
    def is_properly_formatted(cls, v):
        if not isinstance(v, str):
            v = str(v)
        try:
            datetime.strptime(v, "%m-%d-%Y")
        except ValueError:
            v = v.split(" ")[0]
            v = datetime.strptime(v, "%Y-%m-%d").strftime("%m-%d-%Y")
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value = round(self.value, 2)
