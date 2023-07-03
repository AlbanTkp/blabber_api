from datetime import datetime

from sqlalchemy.orm import relationship

from dbconfig import db
from sqlalchemy.sql import func

from models.User import User


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    user_id1 = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_id2 = db.Column(db.Integer, db.ForeignKey('users.id'))
    blocked_user1 = db.Column(db.Boolean, default=False, nullable=False)
    blocked_user2 = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now)

    user1 = relationship("User", foreign_keys=[user_id1], backref="contacts_1")
    user2 = relationship("User", foreign_keys=[user_id2], backref="contacts_2")

    def __repr__(self):
        return f'<Contact {self.id}>'

    def __init__(self, user_id1, user_id2, blocked_user1 = False, blocked_user2 = False):
        self.user_id1 = user_id1
        self.user_id2 = user_id2
        self.blocked_user1 = blocked_user1
        self.blocked_user2 = blocked_user2

    def toDict(self):
        return {
            "id": self.id,
            "user_id1": self.user_id1,
            "user_id2": self.user_id2,
            "blocked_user1": self.blocked_user1,
            "blocked_user2": self.blocked_user2,
            "user1": self.user1.toDict(),
            "user2": self.user2.toDict()
        }
