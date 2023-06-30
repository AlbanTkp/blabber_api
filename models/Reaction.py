from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from dbconfig import db


class Reaction(db.Model):
    __tablename__ = "reactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    emoji = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    message = relationship("Message", back_populates="reactions")

    def __repr__(self):
        return f'<Reaction {self.id}>'

    def __init__(self, user_id, message_id, emoji):
        self.user_id = user_id
        self.message_id = message_id
        self.emoji = emoji

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message_id": self.message_id,
            "emoji": self.emoji
        }
