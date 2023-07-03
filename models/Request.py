from datetime import datetime

from sqlalchemy.orm import relationship

from dbconfig import db
from sqlalchemy.sql import func


class Request(db.Model):
    __tablename__ = "requests"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    accepted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now)

    sender = relationship("User", foreign_keys=[sender_id], backref="my_requests", uselist=False)
    receiver = relationship("User", foreign_keys=[receiver_id], backref="requests_sent_to_me", uselist=False)

    def __repr__(self):
        return f'<Requests {self.id}>'

    def __init__(self, sender_id, receiver_id):
        self.sender_id = sender_id
        self.receiver_id = receiver_id

    def toDict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "accepted": self.accepted,
            "sender": self.sender.toDict(),
            "receiver": self.receiver.toDict(),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
