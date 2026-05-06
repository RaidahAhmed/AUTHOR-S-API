# stores the user module.
from app.extensions import db

from datetime import datetime  # why


# WHAT IS THE MODEL CLASS #inheriting from model class such that we can create columns to be stored in the table for users.
class User(db.Model):
    __tablename__ = "users"
    # now create different columns for the table
    # all datatypes start with a capital letter?
    id = db.Column(db.Integer, primary_key=True)
    # 50 max characters, nullable meaning always required field
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    contact = db.Column(db.String(50), nullable=False, unique=True)
    image = db.Column(db.String(255), nullable=True,)  # why 255, true
    password = db.Column(db.Text(), nullable=False)
    # why true? #sth about authors and users
    biography = db.Column(db.Text(), nullable=True)
    # note that the dts are in pascals..why?
    user_type = db.Column(db.String(20), default='author')
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __init__(self, first_name, last_name, email, contact, password, biography, user_type, image=None):
        super(User, self).__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.contact = contact
        self.image = image
        self.password = password
        self.biography = biography
        self.user_type = user_type

    def get_full_name(self):  # concatenate first and last name
        return f"{self.last_name} {self.first_name}"
