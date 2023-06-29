from middlewares.auth import jwt_middleware
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
from flask import request
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity

from utils.helpers import sendError, sendResponse

app.config['JWT_SECRET_KEY'] = 'votre_clé_secrète'
jwt = JWTManager(app)


@app.post('/users')
def storeUser():
    try:
        firstname = request.json.get('firstname')
        lastname = request.json.get('lastname')
        email = request.json.get('email')
        password = request.json.get('password')
        photo_url = request.json.get('photo_url')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return sendError("Cet utilisateur existe déjà", code=400)

        user = User(firstname=firstname, lastname=lastname, email=email, password=password, photo_url=photo_url)
        user.hash_password()

        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=user.id)

        return sendResponse("SUCCESS", {'access_token': access_token})
    except Exception as e:
        return sendError(str(e), code=500)


@app.post('/login')
def login():
    try:
        email = request.json.get('email')
        password = request.json.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.verify_password(password):
            access_token = create_access_token(identity=user.id)
            return sendResponse("SUCCESS", {'access_token': access_token})
        else:
            return sendError('Identifiants invalides', code=401)
    except Exception as e:
        return sendError(str(e), code=500)


@app.get('/')
@jwt_middleware
def getUser():
    try:
        return sendResponse("SUCCESS", {"user": request.user.to_dict()})
    except Exception as e:
        return sendError(str(e), code=500)


@app.patch('/users')
@jwt_middleware
def updateUser():
    try:
        user = request.user

        user.firstname = request.json.get('firstname', user.firstname)
        user.lastname = request.json.get('lastname', user.lastname)
        user.email = request.json.get('email', user.email)
        user.photo_url = request.json.get('photo_url', user.photo_url)

        db.session.commit()
        return sendResponse("Utilisateur mis à jour avec succès", {'user': user.to_dict()}), 200
    except Exception as e:
        return sendError(str(e), code=500)


if __name__ == "__main__":
    app.run(debug=True)
