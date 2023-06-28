from models.User import User
from dbconfig import app
from dbconfig import db
from flask import jsonify
import json

def toJson(obj):
    return vars(obj)

@app.route("/")
def hello():
    user = User(firstname="toto", lastname="TOTO", email="toto@gmail.com", password="1234", photo_url="azerty")
    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict())


if __name__ == "__main__":
    app.run(debug=True)
