# stores the book module
from app.extensions import db
from datetime import datetime


class Book(db.Model):  # book class is subclass inheriting from super class model
    __tableneme__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    price_unit = db.Column(db.String(50), nullable=False, default='UGX')
    publication_date = db.Column(db.Date, nullable=False)
    isbn = db.Column(db.String(30), nullable=True, unique=True)
    genre = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    # WHY do we need to keep track of the user id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    company = db.relationship('Company', backref='books')  # backref to navigate back from child to parent class
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    def __init__(self, title, pages, price, price_unit, publication_date, isbn, genre, description, image, user_id, company_id,):
        # ensures correct functionality of the ORM
        super(Book, self).__init__()
        self.title = title
        self.price = price
        self.pages = pages
        self.price_unit = price_unit
        self.publication_date = publication_date
        self.isbn = isbn
        self.genre = genre
        self.description = description
        self.image = image
        self.user_id = user_id
        self.company_id = company_id

    def __repr__(self) -> str:
        return f"{self.title}"
