from flask import current_app as app, jsonify
from flask import request
from functools import wraps

from main.classes.mongodb import fetch_data
import jwt
import datetime

from main.utils.constants import USERS_DATABASE
from main.utils.string_utils import JsonResp
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Auth Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200

        token = request.cookies.get('access_token')
        if not token:
            logger.info('No token')
            return jsonify({'message': 'Token is missing'}), 401

        try:
            # Store the decoded token data
            decoded_token = jwt.decode(token, app.config['secret_key'], algorithms=["HS256"])

            # Add the decoded token to the request object so route handlers can access it
            request.user = decoded_token
            # Verify user exists in database (optional but recommended)
            user = fetch_data({"user_id": decoded_token["user_id"]}, USERS_DATABASE)
            if not user:
                logger.info('No user')
                return jsonify({'message': 'User not found'}), 401

            return f(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            logger.info('Expired token')
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            logger.info('Invalid token')
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            logger.error(e)
            return jsonify({'message': str(e)}), 401

    return decorated

def encodeAccessToken(user_id, email, plan):
    try:
        payload = {
            "user_id": user_id,
            "email": email,
            "plan": plan,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=600)
        }
        return jwt.encode(payload, app.config["secret_key"], algorithm="HS256")
    except Exception as e:
        print(f"Access token encoding error: {str(e)}")  # Add logging for debugging
        raise e

def encodeRefreshToken(user_id, email, plan):
    try:
        payload = {
            "user_id": user_id,
            "email": email,
            "plan": plan,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(weeks=4)
        }
        return jwt.encode(payload, app.config["secret_key"], algorithm="HS256")
    except Exception as e:
        print(f"Refresh token encoding error: {str(e)}")  # Add logging for debugging
        raise e


def refreshAccessToken(refresh_token):
    try:
        user = fetch_data({"refresh_token": refresh_token}, USERS_DATABASE)
        if not user or len(user) == 0:
            user = {"_id": 0, "id": 1, "email": 1, "plan": 1}
        if user:
            # Add algorithms parameter to decode
            decoded = jwt.decode(refresh_token, app.config["secret_key"], algorithms=["HS256"])
            new_access_token = encodeAccessToken(decoded["user_id"], decoded["email"], decoded["plan"])
            result = jwt.decode(new_access_token, app.config["secret_key"], algorithms=["HS256"])
            result["new_access_token"] = new_access_token
            resp = JsonResp(result, 200)
        else:
            result = {"message": "Auth refresh token has expired"}
            resp = JsonResp(result, 403)

    except jwt.ExpiredSignatureError:
        result = {"message": "Auth refresh token has expired"}
        resp = JsonResp(result, 403)
    except Exception as e:
        result = {"message": f"Auth error: {str(e)}"}
        resp = JsonResp(result, 403)

    return resp
