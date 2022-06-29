import json
from datetime import datetime
from typing import List, Union

from pydantic import BaseModel, validator


class Transaction(BaseModel):
    title: str
    value: float
    category_id: int = -1
    id: int = None
    user_id: str = None
    created: datetime = None

    @validator("value")
    def has_value(cls, v):
        if not v:
            raise ValueError("value must be a number")
        return v

    @validator("title")
    def has_title(cls, v):
        if not v:
            raise ValueError("title must be a string")
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value = round(self.value, 2)

    @property
    def formatted_date(self):
        return self.created.strftime("%m-%d-%Y")

    @property
    def form_ready_date(self):
        return self.created.strftime("%Y-%m-%d")

    @property
    def formatted_value(self):
        return f"{self.value:,.2f}"

    @property
    def category(self):
        from .db import DBUtils

        return DBUtils.get_category_by_id(self.category_id).label

    @property
    def value_type(self):
        from .db import DBUtils

        if DBUtils.get_category_by_id(self.category_id).is_expense:
            return "Expense"
        return "Income"

    def __lt__(self, other):
        return self.created < other.created


class Category(BaseModel):
    id: int
    label: str
    is_expense: bool
    is_annual: bool
    is_discretionary: bool
    total: float = None

    @property
    def formatted_total(self):
        return f"{self.total:,.2f}"

    def __lt__(self, other):
        return self.total < other.total


class WeightedCategory(BaseModel):
    category_id: int
    weight: int

    def __lt__(self, other):
        return self.weight < other.weight


class CategoryMapping(BaseModel):
    id: int
    word: str
    categories: Union[str, List[WeightedCategory]]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.categories = [WeightedCategory(**c) for c in json.loads(self.categories)]
