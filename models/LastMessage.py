from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from dbconfig import db
from models.File import File


class LastMessage(db.Model):
    __tablename__ = "last_messages"

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'))
    text = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now)

    discussion = relationship("Discussion", back_populates="last_message", uselist=False)
    message = relationship("Message", backref="last_message", uselist=False)

    def __repr__(self):
        return f'<Discussion {self.id}>'

    def __init__(self, sender_id, discussion_id, text):
        self.sender_id = sender_id
        self.discussion_id = discussion_id
        self.text = text

    def toDict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "discussion_id": self.discussion_id,
            "text": self.text,
            "file": self.message.file
        }
