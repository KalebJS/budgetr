import os
from contextlib import suppress

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "budgetr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    with suppress(OSError):
        os.makedirs(app.instance_path)

    from src.database import db

    db.init_app(app)

    from src import auth

    app.register_blueprint(auth.bp)

    from src import budget

    app.register_blueprint(budget.bp)
    app.add_url_rule("/", endpoint="index")

    return app
