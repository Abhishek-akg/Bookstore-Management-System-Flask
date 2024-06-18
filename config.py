import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Docker@1998'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://yourusername:yourpassword@localhost/bookstore'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
