from flask import request, jsonify
from flask_jwt_extended import decode_token, get_jwt_identity, jwt_required
from functools import wraps

from models.User import User
from utils.helpers import sendError


def jwt_middleware(f):
    @jwt_required()
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            token = request.headers.get('Authorization')
            if not token:
                return sendError("Token manquant", code=401)

            # decoded_token = decode_token(token)
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                return sendError("Token incorrect", code=401)
            request.user = user

            return f(*args, **kwargs)

        except Exception as e:
            return sendError(str(e), code=401)

    return decorated_function
