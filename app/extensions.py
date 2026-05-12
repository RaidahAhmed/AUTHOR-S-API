# for creating instances for different 3rd party libraries we'll be working with.

from flask_sqlalchemy import SQLAlchemy #imports sqlalchmey class that creates the database tool.
from flask_migrate import Migrate #Imports flask migrate and registers it.
#SQLAlchemy bridges btn python and sqlalchemy making it simpler to work with databases with out switching btn python and raw SQL.
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

db = SQLAlchemy() #creates an instance of the SQLAlchemy class and stores it in db.
#db now helps define database models, query the database, add,update and delete records, create a database file.
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()