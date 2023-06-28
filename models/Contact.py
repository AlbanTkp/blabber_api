from ..dbconfig import db

from sqlalchemy.sql import func


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id1 = db.Column(db.Integer)
    user_id2 = db.Column(db.Integer)
    blocked_user_id1 = db.Column(db.Integer)
    blocked_user_id2 = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Contact {self.id}>'
