from datetime import datetime

from sqlalchemy.orm import aliased

from dbconfig import db
from sqlalchemy.sql import func
from bcrypt import hashpw, gensalt, checkpw


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100))
    photo_url = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now)

    def __repr__(self):
        return f'<User {self.firstname}>'

    def __init__(self, username, firstname, lastname, email, password, photo_url):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.photo_url = photo_url

    def toDict(self):
        return {
            "id": self.id,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "photo_url": self.photo_url
        }

    def hash_password(self):
        self.password = hashpw(self.password.encode('utf-8'), gensalt())

    def verify_password(self, password):
        return checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def getContacts(self):
        from models.Contact import Contact
        contacts = Contact.query.filter(
            (Contact.user_id1 == self.id) |
            (Contact.user_id2 == self.id)
        ).all()
        return contacts

    def inContactWith(self, user_id):
        from models.Contact import Contact
        contact = Contact.query.filter(
            ((Contact.user_id1 == self.id) & (Contact.user_id2 == user_id)) |
            ((Contact.user_id2 == self.id) & (Contact.user_id1 == user_id))
        ).first()
        if contact:
            return True
        return False

    def getPrivateDiscussionWith(self, user_id):
        from models.Participant import Participant
        from models.Discussion import Discussion
        Participant1 = aliased(Participant)
        Participant2 = aliased(Participant)
        discussion = Discussion.query \
            .join(Participant1, Participant1.discussion_id == Discussion.id) \
            .join(Participant2, Participant2.discussion_id == Discussion.id) \
            .filter(Discussion.tag == "PRIVATE") \
            .filter(((Participant1.user_id == self.id) & (Participant2.user_id == user_id)) | (
                (Participant1.user_id == user_id) & (Participant2.user_id == self.id))) \
            .first()
        return discussion
