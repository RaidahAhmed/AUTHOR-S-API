# stores the user module.
from app.extensions import db

from datetime import datetime

class User(db.Model):
    __tablename__ = "users"
    #create different columns for the table
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False) # 50 max characters, nullable meaning always required field
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    contact = db.Column(db.String(50), nullable=False, unique=True)
    image = db.Column(db.String(255), nullable=True,)
    password = db.Column(db.Text(), nullable=False)
    biography = db.Column(db.Text(), nullable=True)
    user_type = db.Column(db.String(20), default='author')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    def __init__(self, first_name, last_name, email, contact, password, biography, user_type=None, image=None):
        super(User, self).__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.contact = contact
        self.password = password
        self.biography = biography
        self.user_type = user_type
        self.image = image
        

    def get_full_name(self):  # concatenate first and last name
        return f"{self.last_name or ''} {self.first_name or ''}".strip()
