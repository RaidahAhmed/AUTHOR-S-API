# Storing all functions to be used for the user authentication process

from flask import Blueprint, request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN 
import validators
from app.models.users import User
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.extensions import db, bcrypt

#users blueprint
users = Blueprint('users', __name__, url_prefix='/api/v1/users')

#Getting all users from the database
@users.get('/')
@jwt_required()
def getAllUsers():

    try:
        all_users = User.query.all()
        users_data = []

        for user in all_users:
            user_info = {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.get_full_name(),
                "email": user.email,
                "contact": user.contact,
                "type": user.user_type,
                "created_at": user.created_at
            }
            users_data.append(user_info)

        return jsonify({
            "message": "All users retrieved successfully",
            "total_users": len(users_data),
            "users": users_data
        }), HTTP_200_OK

        return jsonify(all_users)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR


@users.get('/authors')
@jwt_required()
def getAllAuthors():

    try:
        all_authors = User.query.filter_by( user_type='author').all()
        authors_data = []

        for author in all_authors:
            author_info = {
                "id": author.id,
                "first_name": author.first_name,
                "last_name": author.last_name,
                "name": author.get_full_name(),
                "email": author.email,
                "contact": author.contact,
                "biography": author.biography,
                "created_at": author.created_at,
                "companies": [],
                "books": []
            }
            if hasattr(author, 'books'):
                author_info['books'] = [{
                        "id": book.id,
                        "title": book.title,
                        "price": book.price,
                        "genre": book.genre,
                        "price_unit": book.price_unit,
                        "description": book.description,
                        "publication_date": book.publication_date,
                        "image": book.image,
                        "created_at": book.created_at
                    }
                    for book in author.books
                ]
            if hasattr(author, 'companies'):
                author_info['companies'] = [{
                        "id": company.id,
                        "name": company.name,
                        "origin": company.origin,
                        "description": company.description,
                    }
                    for company in author.companies
                ]
            authors_data.append(author_info)
        return jsonify({
            "message": "All authors retrieved successfully",
            "total_authors": len(authors_data),
            "authors": authors_data
        }), HTTP_200_OK
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR
    
    #   Get user by id
@users.get('/user/<int:id>')
@jwt_required()
def getUser(id):

    try:
        user = User.query.filter_by(id=id).first()
        books = []
        companies = []

        if hasattr(user, 'books'):
            books = [{
                    "id": book.id,
                    "title": book.title,
                    "price": book.price,
                    "price_unit": book.price_unit,
                    "genre": book.genre,
                    "description": book.description,
                    "publication_date": book.publication_date,
                    "image": book.image,
                    "created_at": book.created_at
                }
                for book in user.books
            ]
        if hasattr(user, 'companies'):
            companies = [{
                    "id": company.id,
                    "name": company.name,
                    "origin": company.origin,
                    "description": company.description
                }
                for company in user.companies
            ]

        if not user:
            return jsonify({
                "message": "User not found"
            }), HTTP_404_NOT_FOUND
        return jsonify({
            "message": "User details retrieved successfully",
            "user":{
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.get_full_name(),
                "email": user.email,
                "contact": user.contact,
                "type": user.user_type,
                "biography": user.biography,
                "created_at": user.created_at,
                "companies": companies,
                "books": books
            }
        }),HTTP_200_OK
    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR

#update user details
@users.route('/edit/<int:user_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def updateUser(user_id):

    try:
        current_user = int(get_jwt_identity())
        logged_in_user = User.query.filter_by(id=current_user).first()
        if not logged_in_user:
            return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"message": "User not found"}), HTTP_404_NOT_FOUND
        
        if logged_in_user.user_type != 'admin' and user.id != current_user:
            return jsonify({"error":"You are not authorized to update user details."}), HTTP_403_FORBIDDEN  #authorization
        
        data = request.get_json()
        if not data:
            return jsonify({"error":"No data provided"})
        #update fields only if provided in request
        user.first_name = data.get("first_name",user.first_name)
        user.last_name = data.get("last_name",user.last_name)
        user.email = data.get("email", user.email)
        user.contact = data.get("contact", user.contact)
        user.biography = data.get("biography", user.biography)
        user.user_type = data.get("user_type", user.user_type)

        if 'password' in data:
            hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            user.password = hashed_password
        
        new_email = data.get("email")

        if new_email and new_email != user.email:
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user:
                return jsonify({"error": "Email already in use"}), HTTP_409_CONFLICT

        db.session.commit()
        
        user_name = user.get_full_name()
        return jsonify({
            "message": f"{user_name}'s details have beed updated successfully!",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "contact": user.contact,
                "biography": user.biography,
                "image": user.image,
                "user_type": user.user_type,
                "updated_at": user.updated_at}
        }), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    
#Delete a user
@users.route('/delete/<int:user_id>', methods=['DELETE'])
@jwt_required()
def deleteUser(user_id):

    try:
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify({"message": "User not found"}), HTTP_404_NOT_FOUND

        current_user = int(get_jwt_identity())
        logged_in_user = User.query.filter_by(id=current_user).first()

        if not logged_in_user:
            return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

        if logged_in_user.user_type != "admin" and current_user != user_id:   #authorization
            return jsonify({"error": "Not authorized to delete this user"}), HTTP_403_FORBIDDEN
        
        from app.models.companies import Company
        Company.query.filter_by(user_id = user.id).delete() #deleting associated companies

        from app.models.books import Book
        Book.query.filter_by(user_id = user.id).delete()


        db.session.delete(user)
        db.session.commit()

        return jsonify({
            "message": "User deleted successfully"
        }), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    
#searching for an author
@users.get('/search')
def searchForAuthor():

    try:
        search_query = request.args.get('query')

        if not search_query:
            return jsonify({
                "message": "Search query is required"
            }), HTTP_400_BAD_REQUEST

        authors = User.query.filter(
            User.user_type == 'author',
            (
                User.first_name.ilike(f'%{search_query}%') |
                User.last_name.ilike(f'%{search_query}%')
            )
        ).all()

        if not authors:
            return jsonify({
                "message": f"No authors found matching '{search_query}'"
            }), HTTP_404_NOT_FOUND

        authors_data = []

        for author in authors:
            authors_data.append({
                "id": author.id,
                "first_name": author.first_name,
                "last_name": author.last_name,
                "author_name": f"{author.first_name} {author.last_name}",
                "email": author.email,
                "contact": author.contact,
                "biography": author.biography,
                "created_at": author.created_at
            })

        return jsonify({
            "message": f"Authors with name {search_query} retrieved successfully",
            "search_query": search_query,
            "total_results": len(authors_data),
            "search_results": authors_data
        }), HTTP_200_OK
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    

