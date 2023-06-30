from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from dbconfig import db


class LastMessage(db.Model):
    __tablename__ = "last_messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'))
    text = db.Column(db.String(100))
    file = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    discussion = relationship("Discussion", back_populates="last_message")

    def __repr__(self):
        return f'<Discussion {self.id}>'

    def __init__(self, sender_id, discussion_id, text, file):
        self.sender_id = sender_id
        self.discussion_id = discussion_id
        self.text = text
        self.file = file

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "discussion_id": self.discussion_id,
            "text": self.text,
            "file": self.file
        }
