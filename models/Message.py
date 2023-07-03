from datetime import datetime

from dbconfig import db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'))
    message_responded_to_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=True)
    text = db.Column(db.String(100))
    reactions = relationship("Reaction", back_populates="message")
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now)

    reactions = relationship("Reaction", backref="message")
    sender = relationship("User", backref="messages", uselist=False)
    discussion = relationship("Discussion", back_populates="messages", uselist=False)
    message_responded_to = relationship("Message", backref="responses", remote_side=[id], uselist=False)
    file = relationship("File", back_populates="message", uselist=False)

    def __repr__(self):
        return f'<Message {self.id}>'

    def __init__(self, sender_id, discussion_id, text, message_responded_to_id):
        self.sender_id = sender_id
        self.discussion_id = discussion_id
        self.text = text
        self.message_responded_to_id = message_responded_to_id

    def toDict(self):
        message = {
            "id": self.id,
            "sender_id": self.sender_id,
            "discussion_id": self.discussion_id,
            "message_responded_to_id": self.message_responded_to_id,
            "text": self.text,
            "reactions": [reaction.toDict() for reaction in self.reactions],
            "file": self.file.toDict()
        }
        if self.message_responded_to_id is not None:
            message["message_responded_to"] = self.message_responded_to
        return message
