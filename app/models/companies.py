# stores company module
from app.extensions import db  # To be able to inherit from the model class

from datetime import datetime


class Company(db.Model):
    __tableneme__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    origin = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    # referring to the users table,since customised #WILL be the parent table. #1:M relationship  because an author can have multiple companies
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='companies')  # why?
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    # not paassing in the id because it is already implemented
    def __init__(self, name, origin, description, user_id):
        super(Company, self).__init__()
        self.name = name
        self.origin = origin
        self.description = description
        self.user_id = user_id

    def __repr__(self) -> (str):
        return f"{self.name} {self.origin}"
