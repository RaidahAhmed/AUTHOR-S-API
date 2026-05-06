#  init.py enables us to initialize and work with different imported modules under the folder app. eg: Flask sqlalchemy, flask migrate.

from flask import Flask  # Imports flask
from app.extensions import db, migrate

# application factory function
# helps us work with different 3rd party libraries and blue prints.
# helps us organize and easily manage code.


def create_app():
    # local variable for "create app", stores flask application.
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

# importing and registering models
    from app.models.users import User
    from app.models.companies import Company
    from app.models.books import Book

    @app.route("/")  # decorator - modifies another function.
    def home():
        return "Author's API project setup"

    return app
