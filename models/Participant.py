from sqlalchemy.orm import relationship

from dbconfig import db
from sqlalchemy.sql import func


class Participant(db.Model):
    __tablename__ = "participants"

    id = db.Column(db.Integer, primary_key=True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_admin = db.Column(db.Boolean, default=False)
    has_new_notif = db.Column(db.Boolean, default=False)
    is_archived_chat = db.Column(db.Boolean, default=False)
    added_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    discussion = relationship("Discussion", back_populates="participants")

    def __repr__(self):
        return f'<Participant {self.id}>'

    def __init__(self, user_id, is_admin):
        self.user_id = user_id
        self.is_admin = is_admin

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "is_admin": self.is_admin,
            "has_new_notif": self.has_new_notif,
            "is_archived_chat": self.is_archived_chat,
            "added_at": self.added_at
        }
