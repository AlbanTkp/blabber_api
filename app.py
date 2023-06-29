from models.User import User
from models.Request import Request
from models.Contact import Contact
from models.Discussion import Discussion
from models.Message import Message
from models.LastMessage import LastMessage
from models.Participant import Participant
from models.Reaction import Reaction
from dbconfig import app
from dbconfig import db
from flask import jsonify
import json

def toJson(obj):
    return vars(obj)

@app.route("/")
def hello():
    db.drop_all()
    # db.create_all()
    # return jsonify(user.to_dict())
    return {}


if __name__ == "__main__":
    app.run(debug=True)
