from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import relationship

from dbconfig import db


class File(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    original_name = db.Column(db.String(80))
    path_url = db.Column(db.String(80))
    size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now)

    message = relationship("Message", back_populates="file", uselist=False)

    def __init__(self, original_name, path_url, size):
        self.original_name = original_name
        self.path_url = path_url
        self.size = size

    def toDict(self):
        return {
            "original_name": self.original_name,
            "path_url": self.path_url,
            "size": self.size
        }
