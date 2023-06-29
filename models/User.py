from dbconfig import db
from sqlalchemy.sql import func
from bcrypt import hashpw, gensalt, checkpw


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
            "id": self.id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "password": self.password,
            "photo_url": self.photo_url
        }

    def hash_password(self):
        self.password = hashpw(self.password.encode('utf-8'), gensalt())

    def verify_password(self, password):
        return checkpw(password.encode('utf-8'), self.password.encode('utf-8'))