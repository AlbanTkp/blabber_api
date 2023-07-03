import os
from datetime import timedelta
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
from flask import request, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token

from models.File import File
from utils.helpers import sendError, sendResponse, renameFile

import traceback

app.config['JWT_SECRET_KEY'] = 'BLABBER'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'uploads'

jwt = JWTManager(app)


@app.post('/users')
def storeUser():
    try:
        username = request.json.get('username')
        firstname = request.json.get('firstname')
        lastname = request.json.get('lastname')
        email = request.json.get('email')
        password = request.json.get('password')
        photo_url = request.json.get('photo_url')
        user = User.query.filter(User.email == email).first()
        if user:
            return sendError("Cet email est déjà utilisé", code=400)

        user = User(username=username, firstname=firstname, lastname=lastname, email=email, password=password,
                    photo_url=photo_url)
        user.hash_password()

        db.session.add(user)
        db.session.commit()
        return sendResponse("Utilisateur créé avec succès", {'user': user.toDict()}, 201)
    except Exception as e:
        return sendError(str(e), data={"trace": traceback.format_exc()}, code=500)


@app.post('/login')
def login():
    try:
        email = request.json.get('email')
        password = request.json.get('password')
        user = User.query.filter(User.email == email).first()
        if user and user.verify_password(password):
            access_token = create_access_token(identity=user.id)
            return sendResponse("SUCCESS", {'access_token': access_token, 'user': user.toDict()})
        else:
            return sendError('Identifiants invalides', code=401)
    except Exception as e:
        return sendError(str(e), code=500)


@app.get('/auth')
@jwt_middleware
def getAuthUser():
    try:
        return sendResponse("SUCCESS", {"user": request.user.toDict()})
    except Exception as e:
        return sendError(str(e), code=500)


@app.patch('/users')
@jwt_middleware
def updateUser():
    try:
        user = request.user

        action = request.form.get('action')
        if action == 'UPDATE_PHOTO':
            if 'file' not in request.files:
                return sendError('Veuillez soumettre un fichier', code=400)
            file = request.files['file']
            if file.filename == '':
                return sendError('Aucun fichier sélectionné', code=400)
            allowed_extensions = ['png', 'jpg', 'jpeg']
            if file.filename.split('.')[-1].lower() not in allowed_extensions:
                return sendError('Type de fichier non autorisé', code=400)
            filename = renameFile(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            user.photo_url = path
            db.session.commit()
            return sendResponse("Photo modifiée avec succès", {'user': user.toDict()})
        elif action == 'UPDATE_INFOS':
            user.username = request.json.get('username', user.username)
            user.firstname = request.json.get('firstname', user.firstname)
            user.lastname = request.json.get('lastname', user.lastname)
            user.email = request.json.get('email', user.email)

            db.session.commit()
            return sendResponse("Utilisateur mis à jour avec succès", {'user': user.toDict()})
        elif action == 'CHANGE_PASSWORD':
            old_pwd = request.json.get('old_password')
            if not user.verify_password(old_pwd):
                return sendError("Ancien mot de passe incorrect", code=403)
            user.password = request.json.get('new_password')
            user.hash_password()
            db.session.commit()
            return sendResponse("Mot de passe mis à jour avec succès")
    except Exception as e:
        return sendError(str(e), data={"trace": traceback.format_exc()}, code=500)


@app.get('/profils/<string:filename>')
@jwt_middleware
def downloadProfileImage(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        return sendError(str(e), code=500)


@app.get('/users/<int:user_id>')
@jwt_middleware
def getUser(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return sendError("Utilisateur non trouvé", code=400)
        return sendResponse("SUCCESS", {"user": user.toDict()})
    except Exception as e:
        return sendError(str(e), code=500)


@app.get('/contacts')
@jwt_middleware
def getAuthContacts():
    try:
        user = request.user
        contacts = [contact.toDict() for contact in user.getContacts()]
        return sendResponse("SUCCESS", {"contacts": contacts})
    except Exception as e:
        return sendError(str(e), code=500)


@app.get('/contacts/<int:contact_id>')
@jwt_middleware
def getContact(contact_id):
    try:
        user = request.user
        contact = Contact.query.get(contact_id)
        if not contact:
            return sendError("Contact non trouvé", code=400)
        if contact.user_id1 != user.id and contact.user_id2 != user.id:
            return sendError("Vous ne pouvez pas accéder aux contacts d'autrui", code=403)
        return sendResponse("SUCCESS", {"contact": contact.toDict()})
    except Exception as e:
        return sendError(str(e), code=500)


@app.delete('/contacts/<int:contact_id>')
@jwt_middleware
def deleteContact(contact_id):
    try:
        user = request.user
        contact = Contact.query.get(contact_id)
        if not contact:
            return sendError("Contact non trouvé", code=400)
        if contact.user_id1 != user.id and contact.user_id2 != user.id:
            return sendError("Vous ne pouvez pas accéder aux contacts d'autrui", code=403)
        db.session.delete(contact)
        db.session.commit()
        return sendResponse("Contact supprimé avec succès")
    except Exception as e:
        return sendError(str(e), code=500)


@app.patch('/contacts/<int:contact_id>')
@jwt_middleware
def setBlockedStatus(contact_id):
    try:
        user = request.user
        is_blocked = request.json.get('is_blocked')
        contact = Contact.query.get(contact_id)
        if not contact:
            return sendError("Contact non trouvé", code=404)
        if contact.user_id1 != user.id and contact.user_id2 != user.id:
            return sendError("Vous ne pouvez pas accéder aux contacts d'autrui", code=403)

        if contact.user_id1 == user.id:
            contact.blocked_user2 = is_blocked
        else:
            contact.blocked_user1 = is_blocked
        db.session.commit()
        return sendResponse("Contact bloqué avec succès", {"contact": contact.toDict()})
    except Exception as e:
        return sendError(str(e), code=500)


@app.post('/discussions')
@jwt_middleware
def storeDiscussion():
    try:
        user = request.user
        tag = request.json.get('tag')
        if tag == 'PRIVATE':
            user_id = request.json.get('user_id')
            discussion = user.getPrivateDiscussionWith(user_id)
            if discussion:
                return sendError("Vous avez déjà une discussion privée avec cet utilisateur",
                                 {'discussion': discussion.toDict()}, code=403)
            if not user.inContactWith(user_id):
                return sendError("Cet utilisateur ne fait pas partie de vos contacts", code=403)
            discussion = Discussion(tag=tag, created_by_id=user.id)
            participant1 = Participant(user_id=user.id, discussion_id=discussion.id, is_admin=False)
            participant2 = Participant(user_id=user_id, discussion_id=discussion.id, is_admin=False)
            discussion.participants.append(participant1)
            discussion.participants.append(participant2)
            db.session.add(discussion)
            db.session.commit()
            return sendResponse("Discussion privée créée avec succès", {'discussion': discussion.toDict()}, 201)
        elif tag == 'GROUP':
            name = request.json.get('name')
            description = request.json.get('description')

            discussion = Discussion(tag=tag, created_by_id=user.id, name=name, description=description)

            user_ids = request.json.get('participants')
            for user_id in user_ids:
                is_admin = False
                if user_id == user.id:
                    is_admin = True
                participant = Participant(user_id=user_id, discussion_id=discussion.id, is_admin=is_admin,
                                          has_new_notif=True)
                discussion.participants.append(participant)

            db.session.add(discussion)
            db.session.commit()
            return sendResponse("Discussion de groupe créée avec succès", {'discussion': discussion.toDict()})

    except Exception as e:
        return sendError(str(e), data={"trace": traceback.format_exc()}, code=500)


@app.patch('/discussions/<int:discussion_id>')
@jwt_middleware
def updateDiscussion(discussion_id):
    try:
        user = request.user
        action = request.json.get('action')
        discussion = Discussion.query.get(discussion_id)
        if not discussion:
            return sendError("Discussion non trouvée", code=404)

        participant_auth = Participant.query.filter(
            (Participant.user_id == user.id) &
            (Participant.discussion_id == discussion_id)
        ).first()
        if not participant_auth:
            return sendError("Vous n'avez pas accès à cette discussion", code=403)

        if action == "ARCHIVED":
            is_archived = request.json.get('is_archived')
            participant_auth.is_archived_chat = is_archived
            db.session.commit()
            return sendResponse("Discussion " + ("archivée" if is_archived else "désarchivée") + " avec succès",
                                {"discussion": discussion.toDict()})
        elif action == 'UPDATE_GROUP_INFO':
            if discussion.tag != 'GROUP':
                return sendError("Il ne s'agit pas d'un groupe", code=403)
            discussion.name = request.json.get('name')
            discussion.description = request.json.get('description')
            db.session.commit()
            return sendResponse("Groupe modifié avec succès", {"group": discussion.toDict()})
        elif action == 'DEFINE_ADMINS_GROUP':
            if discussion.tag != 'GROUP':
                return sendError("Il ne s'agit pas d'un groupe", code=403)
            if not participant_auth.is_admin:
                return sendError("Vous devez être administrateur pour effectuer cette action", code=403)
            user_ids = request.json.get('users')
            participants = Participant.query.filter(
                (Participant.user_id.in_(user_ids)) &
                (Participant.discussion_id == discussion_id)
            ).all()
            for participant in participants:
                participant.is_admin = True
            db.session.commit()
            return sendResponse("Administrateurs de groupe modifiés avec succès", {"group": discussion.toDict()})
        elif action == 'ADD_USERS_GROUP':
            if discussion.tag != 'GROUP':
                return sendError("Il ne s'agit pas d'un groupe", code=403)
            if not participant_auth.is_admin:
                return sendError("Vous devez être administrateur pour effectuer cette action", code=403)
            user_ids = request.json.get('users')
            for user_id in user_ids:
                participant = Participant(user_id, discussion_id, False)
                discussion.participants.append(participant)
            db.session.commit()
            return sendResponse("Participants ajoutés au groupe avec succès", {"group": discussion.toDict()})
        elif action == 'REMOVE_USERS_GROUP':
            if discussion.tag != 'GROUP':
                return sendError("Il ne s'agit pas d'un groupe", code=403)
            if not participant_auth.is_admin:
                return sendError("Vous devez être administrateur pour effectuer cette action", code=403)
            user_ids = request.json.get('users')
            participants = Participant.query.filter(
                (Participant.user_id.in_(user_ids)) &
                (Participant.discussion_id == discussion_id)
            ).all()
            for participant in participants:
                db.session.delete(participant)
            db.session.commit()
            return sendResponse("Participants supprimés du groupe avec succès", {"group": discussion.toDict()})
        elif action == 'LEAVE_GROUP':
            if discussion.tag != 'GROUP':
                return sendError("Il ne s'agit pas d'un groupe", code=403)
            participant_auth = Participant.query.filter(
                (Participant.user_id == user.id) &
                (Participant.discussion_id == discussion_id)
            ).first()
            if not participant_auth:
                return sendError("Vous n'avez pas accès à cette discussion", code=403)
            db.session.delete(participant_auth)
            db.session.commit()
            return sendResponse("Vous avez quitté le groupe")

    except Exception as e:
        return sendError(str(e), code=500)


@app.get('/discussions/<int:discussion_id>')
@jwt_middleware
def getDiscussion(discussion_id):
    try:
        user = request.user
        discussion = Discussion.query.get(discussion_id)
        if not discussion:
            return sendError("Discussion non trouvée", code=404)
        participant = Participant.query.filter(
            (Participant.user_id == user.id) &
            (Participant.discussion_id == discussion_id)
        ).first()
        if not participant:
            return sendError("Vous n'avez pas accès à cette discussion", code=403)

        return sendResponse("SUCCESS", {"discussion": discussion.toDict()})
    except Exception as e:
        return sendError(str(e), code=500)


@app.delete('/discussions/<int:discussion_id>')
@jwt_middleware
def deleteDiscussion(discussion_id):
    try:
        user = request.user
        discussion = Discussion.query.get(discussion_id)
        if not discussion:
            return sendError("Discussion non trouvée", code=404)
        participant = Participant.query.filter(
            (Participant.user_id == user.id) &
            (Participant.discussion_id == discussion_id)
        ).first()
        if not participant:
            return sendError("Vous n'avez pas accès à cette discussion", code=403)
        if not participant.is_admin:
            return sendError("Vous devez être administrateur pour effectuer cette action", code=403)
        db.session.delete(discussion)
        db.session.commit()
        return sendResponse("Discussion supprimée avec succès")
    except Exception as e:
        return sendError(str(e), code=500)


@app.get('/discussions')
@jwt_middleware
def getDiscussions():
    try:
        user = request.user
        discussions = Discussion.query \
            .join(Participant, Participant.discussion_id == Discussion.id) \
            .filter(Participant.user_id == user.id) \
            .all()
        return sendResponse("SUCCESS", {"discussions": [discussion.toDict() for discussion in discussions]})
    except Exception as e:
        return sendError(str(e), code=500)


@app.get('/users')
@jwt_middleware
def getUsers():
    try:
        user = request.user
        users = User.query.filter(User.id != user.id)

        params = request.args
        limit = params.get("limit")
        skip = params.get("skip")
        sort_by = params.get("sort_by")
        sort_by_order = params.get("sort_by_order")
        paginate = params.get("paginate")
        sort_by = params.get("sort_by")
        sort_by = params.get("sort_by")

        users = users.get()
        return sendResponse("SUCCESS", {"users": [user.toDict() for user in users]})
    except Exception as e:
        return sendError(str(e), code=500)



@app.get('/users/<int:user_id>/discussion')
@jwt_middleware
def getDiscussionWithUser(user_id):
    try:
        user = request.user
        discussion = getDiscussionWithUser(user_id)
        return sendResponse("SUCCESS", {"discussion": discussion.toDict() if discussion else None})
    except Exception as e:
        return sendError(str(e), code=500)


@app.get('/discussions/<int:discussion_id>/messages')
@jwt_middleware
def getDiscussionMessages(discussion_id):
    try:
        user = request.user
        discussion = Discussion.query.get(discussion_id)
        if not discussion:
            return sendError("Cette discussion n'existe pas", code=404)
        if not discussion.isUserParticipant(user.id):
            return sendError("Vous n'avez pas accès à la discussion", code=500)
        messages = discussion.messages

        return sendResponse("SUCCESS", {"messages": [message.toDict() for message in messages]})
    except Exception as e:
        return sendError(str(e), code=500)


@app.post('/messages')
@jwt_middleware
def storeMessage():
    try:
        user = request.user
        text = request.form.get('text')
        discussion_id = request.form.get('discussion_id')
        message_responded_to_id = request.form.get('message_responded_to_id', None)
        file = None

        discussion = Discussion.query.get(discussion_id)
        if not discussion:
            return sendError("Discussion non trouvée", code=404)
        if not discussion.isUserParticipant(user.id):
            return sendError("Vous n'êtes pas un participant de cette discussion")

        message = Message(sender_id=user.id, discussion_id=discussion_id, text=text,
                          message_responded_to_id=message_responded_to_id)
        if discussion.last_message:
            discussion.last_message.sender_id = user.id
            discussion.last_message.text = text
        else:
            discussion.last_message = LastMessage(sender_id=user.id, discussion_id=discussion_id, text=text)

        if 'file' in request.files:
            r_file = request.files['file']
            if r_file.filename == '':
                return sendError('Aucun fichier sélectionné', code=400)
            # allowed_extensions = ['png', 'jpg', 'jpeg']
            # if file.filename.split('.')[-1].lower() not in allowed_extensions:
            #     return sendError('Type de fichier non autorisé', code=400)
            filename = renameFile(r_file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            r_file.save(path)
            file = File(r_file.filename, path, os.path.getsize(path))
            message.file = file
            discussion.last_message.message = message

        db.session.add(message)
        db.session.commit()
        return sendResponse("Message créé avec succès", {"message": message.toDict()}, 201)
    except Exception as e:
        return sendError(str(e), data={"trace": traceback.format_exc()}, code=500)


@app.patch('/messages/<int:message_id>')
@jwt_middleware
def updateMessage(message_id):
    try:
        user = request.user
        action = request.json.get('action')
        message = Message.query.get(message_id)
        if not message:
            return sendError('Message non trouvé', code=404)
        if action == 'EMOJI_REACTION':
            if not message.discussion.isUserParticipant(user.id):
                return sendError("Vous n'êtes pas un participant de cette discussion", code=403)
            emoji = request.json.get('emoji')
            reaction = Reaction.query.filter(
                (Reaction.user_id == user.id) & (Reaction.message_id == message.id)).first()
            if reaction:
                reaction.emoji = emoji
            else:
                message.reactions.append(Reaction(user_id=user.id, message_id=message.id, emoji=emoji))
            db.session.commit()
        return sendResponse("SUCCES", {"message": message.toDict()})

    except Exception as e:
        return sendError(str(e), code=500)


@app.get('/messages/<int:message_id>/file')
@jwt_middleware
def downloadMessageFile(message_id):
    try:
        message = Message.query.get(message_id)
        if not message:
            return sendError("Message non trouvé", code=404)
        filename = message.file.path_url.split('/')[-1]
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        return sendError(str(e), code=500)


@app.get('/requests')
@jwt_middleware
def getRequestsSentToMe():
    try:
        user = request.user
        rqs = []
        for r in user.requests_sent_to_me:
            if not r.accepted:
                rqs.append(r.toDict())
        return sendResponse("SUCCES", {"requests": rqs})
    except Exception as e:
        return sendError(str(e), code=500)


@app.post('/requests')
@jwt_middleware
def storeRequest():
    try:
        user = request.user
        receiver_id = request.json.get("user_id")
        if user.id == receiver_id:
            return sendError("Vous ne pouvez pas vous envoyer de requête", code=403)

        rq = Request.query.filter(
            ((Request.sender_id == user.id) & (Request.receiver_id == receiver_id)) |
            ((Request.sender_id == receiver_id) & (Request.receiver_id == user.id))
        ).filter(Request.accepted == False).first()
        if rq:
            return sendError("Une requête entre vous et cet utilisateur existe déjà", data={"request": rq.toDict()},
                             code=403)
        if user.inContactWith(receiver_id):
            return sendError("Cet utilisateur fait déjà partie de vos contacts", code=403)
        rq = Request(sender_id=user.id, receiver_id=receiver_id)
        db.session.add(rq)
        db.session.commit()
        return sendResponse("Requête créée avec succès", {"request": rq.toDict()}, 201)
    except Exception as e:
        return sendError(str(e), data={"trace": traceback.format_exc()}, code=500)


@app.patch('/requests/<int:request_id>')
@jwt_middleware
def updateRequest(request_id):
    try:
        user = request.user
        accepted = request.json.get('accepted')
        rq = Request.query.get(request_id)
        if not rq:
            return sendError("Requête non trouvée", code=404)
        if rq.accepted:
            return sendError("Cette requête a déjà été acceptée", code=400)
        if rq.receiver_id != user.id:
            return sendError("Cette requête ne vous est pas destinée", code=403)
        if accepted:
            rq.accepted = True
            contact = Contact(user.id, rq.sender_id)
            db.session.add(contact)
            db.session.commit()
            return sendResponse("Requête acceptée avec succès",
                                {"request": rq.toDict()})
        else:
            db.session.delete(rq)
            db.session.commit()
            return sendResponse("Requête rejetée avec succès")
    except Exception as e:
        return sendError(str(e), data={"trace": traceback.format_exc()}, code=500)


if __name__ == "__main__":
    app.run(debug=True)
