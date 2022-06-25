from flask import Blueprint, render_template, request, flash, url_for, redirect
from pydantic import ValidationError

from budgetr.db import get_db
from .models import Transaction

bp = Blueprint("budget", __name__)


@bp.route("/", methods=("GET", "POST"))
def index():
    db = get_db()

    if request.method == "POST":
        try:
            transaction = Transaction(**request.form)
            db.execute(
                "INSERT INTO expense_income (user_id, title, value, category, value_type) VALUES "
                "('kalebjs', ?, ?, ?, ?);",
                (transaction.title, transaction.value, transaction.category, transaction.value_type),
            )
            db.commit()
        except ValidationError as e:
            flash(str(e))

    exp_inc_list = db.execute(
        "SELECT * FROM expense_income WHERE created BETWEEN datetime('now', 'start of month') AND "
        "datetime('now', 'localtime', '+1 day');"
    ).fetchall()
    transactions = [Transaction(**row) for row in exp_inc_list]
    return render_template("budget/index.html", transactions=transactions)


@bp.route("/edit/<int:transaction_id>", methods=("GET", "POST"))
def edit(transaction_id):
    db = get_db()

    if request.method == "POST":
        try:
            transaction = Transaction(**request.form)
            db.execute(
                "UPDATE expense_income SET title = ?, value = ?, category = ?, value_type = ?, created = ? WHERE "
                "id = ?;",
                (
                    transaction.title,
                    transaction.value,
                    transaction.category,
                    transaction.value_type,
                    transaction.created,
                    transaction_id,
                ),
            )
            db.commit()
        except ValidationError as e:
            flash(str(e))

    transaction = Transaction(**db.execute(
        "SELECT * FROM expense_income WHERE id = ?;", (transaction_id,)
    ).fetchone())
    return render_template("budget/edit.html", transaction=transaction)


@bp.route("/delete/<int:transaction_id>", methods=("GET",))
def delete(transaction_id):
    db = get_db()
    db.execute("DELETE FROM expense_income WHERE id = ?;", (transaction_id,))
    db.commit()
    return redirect(url_for("index"))

