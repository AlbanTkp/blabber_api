from dbconfig import db
from sqlalchemy.sql import func


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id1 = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_id2 = db.Column(db.Integer, db.ForeignKey('users.id'))
    blocked_user_id1 = db.Column(db.Integer, db.ForeignKey('users.id'))
    blocked_user_id2 = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Contact {self.id}>'

    def __init__(self, user_id1, user_id2, blocked_user_id1, blocked_user_id2):
        self.user_id1 = user_id1
        self.user_id2 = user_id2
        self.blocked_user_id1 = blocked_user_id1
        self.blocked_user_id2 = blocked_user_id2

    def to_dict(self):
        return {
            "id": self.id,
            "user_id1": self.user_id1,
            "user_id2": self.user_id2,
            "blocked_user_id1": self.blocked_user_id1,
            "blocked_user_id2": self.blocked_user_id2
        }
