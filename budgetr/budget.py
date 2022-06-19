from flask import Blueprint, render_template, request, url_for, redirect, flash
from pydantic import BaseModel, validator, ValidationError

from db import get_db

bp = Blueprint('budget', __name__)


class Transaction(BaseModel):
    title: str
    value: float
    category: str
    value_type: str

    @validator('value_type')
    def has_value_type(cls, v):
        if not v:
            raise ValueError('value_type must be income or expense')
        return v

    @validator('value')
    def has_value(cls, v):
        if not v:
            raise ValueError('value must be a number')
        return v

    @validator('category')
    def has_category(cls, v):
        if not v:
            raise ValueError('category must be a string')
        return v

    @validator('title')
    def has_title(cls, v):
        if not v:
            raise ValueError('title must be a string')
        return v


@bp.route('/', methods=('GET', 'POST'))
def index():
    db = get_db()

    if request.method == "POST":
        try:
            transaction = Transaction(**request.form)
            db.execute(
                "INSERT INTO expense_income (user_id, title, value, category, value_type) VALUES ('kalebjs', ?, ?, ?, ?);",
                (transaction.title, transaction.value, transaction.category, transaction.value_type)
            )
            db.commit()
        except ValidationError as e:
            flash(str(e))

    exp_inc = db.execute(
        "SELECT * FROM expense_income WHERE created BETWEEN datetime('now', 'start of month') AND "
        "datetime('now', 'localtime', '+1 day');"
    ).fetchall()
    return render_template('budget/index.html', exp_inc=exp_inc)
