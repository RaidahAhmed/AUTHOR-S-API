class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/flask_authors_db'
    JWT_SECRET_KEY = "my_very_secret_author"