from dbconfig import db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Discussion(db.Model):
    __tablename__ = "discussions"

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.Enum('PRIVATE', 'GROUP'))
    name = db.Column(db.String(100))
    description = db.Column(db.String(80))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    participants = relationship("Participant", back_populates="discussion")
    last_message = relationship("LastMessage", back_populates="discussion")
    messages = relationship("Message", back_populates="discussion")

    def __repr__(self):
        return f'<Discussion {self.id}>'

    def __init__(self, tag, name, description):
        self.tag = tag
        self.name = name
        self.description = description

    def setParticipants(self, participants):
        self.participants = participants

    def setLastMessage(self, lastMessage):
        self.lastMessage = lastMessage

    def to_dict(self):
        return {
            "id": self.id,
            "tag": self.user_id1,
            "name": self.user_id2,
            "description": self.description,
            "participants": self.participants,
            "lastMessage": self.lastMessage
        }
