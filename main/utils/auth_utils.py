from flask import current_app as app, jsonify
from flask import request
from functools import wraps

from classes.mongodb import fetch_data
import jwt
import datetime

from utils.constants import USERS_DATABASE
from utils.string_utils import JsonResp


# Auth Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        access_token = request.headers.get('accesstoken')

        try:
            data = jwt.decode(access_token, app.config["secret_key"])
        except Exception as e:
            return JsonResp({"message": "Token is invalid", "exception": str(e)}, 401)

        return f(*args, **kwargs)

    return decorated


def encodeAccessToken(user_id, email, plan):
    try:
        accessToken = jwt.encode({
            "user_id": user_id,
            "email": email,
            "plan": plan,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)  # The token will expire in 15 minutes
        }, app.config["secret_key"], algorithm="HS256")
    except Exception as e:
        raise Exception(e)

    return accessToken


def encodeRefreshToken(user_id, email, plan):
    refreshToken = jwt.encode({
        "user_id": user_id,
        "email": email,
        "plan": plan,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(weeks=4)  # The token will expire in 4 weeks
    }, app.config["secret_key"], algorithm="HS256")

    return refreshToken


def refreshAccessToken(refresh_token):
    # If the refresh_token is still valid, create a new access_token and return it
    try:
        user = fetch_data({"refresh_token": refresh_token}, USERS_DATABASE)
        if not user or len(user) == 0:
            user = {"_id": 0, "id": 1, "email": 1, "plan": 1}
        if user:
            decoded = jwt.decode(refresh_token, app.config["secret_key"])
            new_access_token = encodeAccessToken(decoded["user_id"], decoded["email"], decoded["plan"])
            result = jwt.decode(new_access_token, app.config["secret_key"])
            result["new_access_token"] = new_access_token
            resp = JsonResp(result, 200)
        else:
            result = {"message": "Auth refresh token has expired"}
            resp = JsonResp(result, 403)

    except:
        result = {"message": "Auth refresh token has expired"}
        resp = JsonResp(result, 403)

    return resp
