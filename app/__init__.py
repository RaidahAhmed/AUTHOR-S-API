#  init.py enables us to initialize and work with different imported modules under the folder app. eg: Flask sqlalchemy, flask migrate.

from flask import Flask  # Imports flask
from app.extensions import db, migrate, jwt
from app.controllers.auth.auth_controller import auth
from app.controllers.users.user_controller import users
from app.controllers.companies.companies_controller import companies
from app.controllers.books.books_controllers import books

# application factory function
# helps us work with different 3rd party libraries and blue prints.
# helps us organize and easily manage code.


def create_app():

    app = Flask(__name__) #stores flask application.
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

# importing and registering models
    from app.models.users import User
    from app.models.companies import Company
    from app.models.books import Book

    #registering the blueprints
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(companies)
    app.register_blueprint(books)

    @app.route("/")  # decorator - modifies another function.
    def home():
        return "Author's API project setup"

    return app
