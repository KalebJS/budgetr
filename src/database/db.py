import sqlite3
from functools import cache
from typing import List

import click
from flask import current_app, g
from flask.cli import with_appcontext

from .models import Category


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


class DBUtils:
    @staticmethod
    @cache
    def get_category_by_id(category_id: int) -> Category:
        db = get_db()
        result = db.execute(
            "SELECT * FROM categories WHERE id = ?;",
            (category_id,),
        ).fetchone()
        return Category(**result)

    @staticmethod
    def get_categories() -> List[Category]:
        db = get_db()
        results = db.execute("SELECT * FROM categories;").fetchall()
        return [Category(**result) for result in results if result["id"] != -1]

    @staticmethod
    def get_total_by_category() -> List[Category]:
        db = get_db()
        categories = DBUtils.get_categories()
        for category in categories:
            # within the last month and matching category id
            category.total = db.execute(
                "SELECT SUM(value) FROM transactions WHERE created BETWEEN datetime('now', 'start of month') AND "
                "datetime('now', 'localtime', '+1 day') AND category_id = ?;",
                (category.id,),
            ).fetchone()[0]
            if not category.total:
                category.total = 0

        return categories
