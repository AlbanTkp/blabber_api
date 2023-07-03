import json
from datetime import datetime

from dbconfig import db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Discussion(db.Model):
    __tablename__ = "discussions"

    id = db.Column(db.Integer, primary_key=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tag = db.Column(db.Enum('PRIVATE', 'GROUP'))
    name = db.Column(db.String(100))
    description = db.Column(db.String(80))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now)

    participants = relationship("Participant", back_populates="discussion")
    last_message = relationship("LastMessage", back_populates="discussion", uselist=False)
    messages = relationship("Message", back_populates="discussion")

    def __repr__(self):
        return f'<Discussion {self.id}>'

    def __init__(self, tag, created_by_id, name=None, description=None, participants=[], messages=[], last_message=None):
        self.tag = tag
        self.created_by_id = created_by_id
        self.name = name
        self.description = description
        self.participants = participants
        self.messages = messages
        self.last_message = last_message

    def toDict(self):
        discussion = {
            "id": self.id,
            "tag": self.tag,
            "name": self.name,
            "description": self.description,
            "participants": [participant.toDict() for participant in self.participants],
            "last_message": self.last_message
        }
        if self.tag == 'GROUP':
            discussion['created_by_id'] = self.created_by_id
        return discussion

    def isUserParticipant(self, user_id):
        for participant in self.participants:
            if participant.user_id == user_id:
                return True
        return False
