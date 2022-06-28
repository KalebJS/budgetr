from datetime import datetime

from flask import Blueprint, render_template, request, flash, url_for, redirect
from pydantic import ValidationError

from src.classifier import update_classification, classify
from src.database.db import get_db, DBUtils
from src.database.models import Transaction

bp = Blueprint("budget", __name__)


@bp.route("/", methods=("GET", "POST"))
def index():
    db = get_db()

    if request.method == "POST":
        try:
            transaction = Transaction(**request.form)
            transaction = classify(transaction)
            db.execute(
                "INSERT INTO transactions (user_id, title, value, category_id) VALUES "
                "('kalebjs', ?, ?, ?);",
                (transaction.title, transaction.value, transaction.category_id),
            )
            db.commit()
        except ValidationError as e:
            flash(str(e))
            raise e

    exp_inc_list = db.execute(
        "SELECT * FROM transactions WHERE created BETWEEN datetime('now', 'start of month') AND "
        "datetime('now', 'localtime', '+1 day');"
    ).fetchall()
    transactions = [Transaction(**row) for row in exp_inc_list]
    categories = DBUtils.get_total_by_category()
    sorted_categories = sorted([c for c in categories if c.total > 0], reverse=True)
    return render_template(
        "budget/index.html", transactions=transactions, categories=categories, sorted_categories=sorted_categories
    )


@bp.route("/edit/<int:transaction_id>", methods=("GET", "POST"))
def edit(transaction_id):
    db = get_db()

    transaction = Transaction(**db.execute("SELECT * FROM transactions WHERE id = ?;", (transaction_id,)).fetchone())
    if request.method == "POST":
        try:
            updated = Transaction(**request.form)
            update_classification(transaction, updated)
            updated.created = datetime.strptime(request.form["date"], "%Y-%m-%d")
            db.execute(
                "UPDATE transactions SET title = ?, value = ?, category_id = ?, created = ? WHERE "
                "id = ?;",
                (
                    updated.title,
                    updated.value,
                    updated.category_id,
                    updated.created,
                    transaction_id,
                ),
            )
            db.commit()
            transaction = updated
        except ValidationError as e:
            flash(str(e))

    categories = DBUtils.get_categories()
    return render_template("budget/edit.html", transaction=transaction, categories=categories)


@bp.route("/delete/<int:transaction_id>", methods=("GET",))
def delete(transaction_id):
    db = get_db()
    db.execute("DELETE FROM transactions WHERE id = ?;", (transaction_id,))
    db.commit()
    return redirect(url_for("index"))
