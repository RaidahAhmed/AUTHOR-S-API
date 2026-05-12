from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.books import Book
from app.models.companies import Company
from app.models.users import User
from app.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_403_FORBIDDEN

#books blueprint
books = Blueprint('books', __name__, url_prefix='/api/v1/books')

#creating a book
@books.route('/create', methods=['POST'])
@jwt_required()
def createBook():
    try:
        data = request.get_json() or {}

        title = data.get('title')
        pages = data.get('pages')
        publication_date = data.get('publication_date')
        price = data.get('price')
        price_unit = data.get('price_unit')
        description = data.get('description')
        genre = data.get('genre')
        isbn = data.get('isbn')
        company_id = data.get('company_id')
        image = data.get('image')

        user_id = int(get_jwt_identity())

        if not all([title, pages, publication_date, price, price_unit, description, genre, isbn, company_id]):
            return jsonify({"error": "All fields are required"}), HTTP_400_BAD_REQUEST
        
        if Book.query.filter_by(title=title, user_id=user_id).first() is not None:
            return jsonify({"error": "Book with this title and user_id already exists."}), HTTP_409_CONFLICT

        company = Company.query.filter_by(id=company_id).first()
        if not company:
            return jsonify({"error": "Company not found"}), HTTP_404_NOT_FOUND

        if Book.query.filter_by(isbn=isbn).first():
            return jsonify({"error": "Book with this ISBN already in use"}), HTTP_409_CONFLICT

        new_book = Book(
            title=title,
            pages=pages,
            publication_date=publication_date,
            price=price,
            price_unit=price_unit,
            description=description,
            genre=genre,
            isbn=isbn,
            company_id=company_id,
            user_id=user_id,
            image=image)

        db.session.add(new_book)
        db.session.commit()

        return jsonify({
            "message": f"Book '{title}' created successfully",
            "book": {
                "id": new_book.id,
                "title": new_book.title,
                "isbn": new_book.isbn,
                "user_id": new_book.user_id,
                "company_id": new_book.company_id}
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


#getting all books
@books.route('/', methods=['GET'])
@jwt_required()
def getAllBooks():
    try:
        books = Book.query.all()

        result = []

        for book in books:
            result.append({
                "id": book.id,
                "title": book.title,
                "isbn": book.isbn,
                "price": book.price,
                "genre": book.genre,
                "user_id": book.user_id,
                "company_id": book.company_id})

        return jsonify({
            "message": "Books retrieved successfully",
            "total": len(result),
            "books": result
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


#get book by id
@books.route('/<int:book_id>', methods=['GET'])
@jwt_required()
def getBookById(book_id):
    try:
        book = Book.query.filter_by(id=book_id).first()

        if not book:
            return jsonify({"message": "Book not found"}), HTTP_404_NOT_FOUND

        return jsonify({
            "message": "Book details retrieved successfully",
            "book": {
                "id": book.id,
                "title": book.title,
                "isbn": book.isbn,
                "price": book.price,
                "description": book.description,
                "genre": book.genre,
                "user_id": book.user_id,
                "company_id": book.company_id}
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


#updating a book
@books.route('update/<int:book_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def updateBookDetails(book_id):
    try:
        data = request.get_json() or {}

        book = Book.query.filter_by(id=book_id).first()
        if not book:
            return jsonify({"message": "Book not found"}), HTTP_404_NOT_FOUND

        current_user = int(get_jwt_identity())
        logged_in_user = User.query.filter_by(id=current_user).first()

        if not logged_in_user:
            return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

        if logged_in_user.user_type != "admin" and book.company.user_id != current_user:
            return jsonify({"error": "You are not authorised to update this book"}), HTTP_403_FORBIDDEN

        # duplicate checks
        new_isbn = data.get("isbn")
        new_title = data.get("title")

        if new_isbn and new_isbn != book.isbn:
            if Book.query.filter_by(isbn=new_isbn).first():
                return jsonify({"error": "ISBN already exists"}), HTTP_409_CONFLICT

        if new_title and new_title != book.title:
            if Book.query.filter_by(title=new_title, user_id=current_user).first():
                return jsonify({"error": "Book title already exists"}), HTTP_409_CONFLICT

        #fields to be updated
        book.title = data.get("title", book.title)
        book.pages = data.get("pages", book.pages)
        book.price = data.get("price", book.price)
        book.price_unit = data.get("price_unit", book.price_unit)
        book.description = data.get("description", book.description)
        book.genre = data.get("genre", book.genre)
        book.isbn = data.get("isbn", book.isbn)
        book.image = data.get("image", book.image)
        book.publication_date = data.get("publication_date", book.publication_date)

        db.session.commit()

        return jsonify({
            "message": f"{book.title} updated successfully",
            "book": {
                "id": book.id,
                "title": book.title,
                "isbn": book.isbn,
                "price": book.price,
                "pages": book.pages,
                "genre": book.genre,
                "description": book.description,
                "image": book.image,
                "updated_at": book.updated_at,

                # author
                "user": {
                    "id": book.company.user.id,
                    "first_name": book.company.user.first_name,
                    "last_name": book.company.user.last_name,
                    "email": book.company.user.email,
                    "contact": book.company.user.contact,
                    "user_type": book.company.user.user_type
                } if book.company.user else None,

                # Company
                "company": {
                    "id": book.company.id,
                    "name": book.company.name,
                    "origin": book.company.origin,
                    "description": book.company.description,
                    "created_at": book.company.created_at,
                    "updated_at": book.company.updated_at
                } if book.company else None}
        }), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# DELETING A BOOK
@books.route('delete/<int:book_id>', methods=['DELETE'])
@jwt_required()
def deleteBook(book_id):
    try:
        current_user = int(get_jwt_identity())

        book = Book.query.get(book_id)
        if not book:
            return jsonify({"message": "Book not found"}), HTTP_404_NOT_FOUND

        logged_in_user = User.query.get(current_user)

        if not logged_in_user:
            return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

        if logged_in_user.user_type != "admin" and book.company.user_id != current_user:
            return jsonify({"error": "You are not authorised to delete this book"}), HTTP_403_FORBIDDEN

        db.session.delete(book)
        db.session.commit()

        return jsonify({
            "message": f"Book '{book.title}' deleted successfully"
        }), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR