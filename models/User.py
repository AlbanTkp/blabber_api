from dbconfig import db
# import pymysql
from sqlalchemy.sql import func


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100))
    photo_url = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<User {self.firstname}>'

    def __init__(self, firstname, lastname, email, password, photo_url):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.photo_url = photo_url

    def to_dict(self):
        return {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "password": self.password,
            "photo_url": self.photo_url
        }