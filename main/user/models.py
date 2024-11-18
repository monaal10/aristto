from enum import Enum
from json import JSONDecodeError

from flask import current_app as app, request
from flask import json
import jwt
from passlib.hash import pbkdf2_sha256

from classes.mongodb import fetch_data, update_data, insert_data
from utils import string_utils
from utils.auth_utils import encodeAccessToken, encodeRefreshToken
from utils.constants import USERS_DATABASE, MONGODB_SET_OPERATION, MONGODB_UNSET_OPERATION
from bson import ObjectId

class Plan(Enum):
    BASIC = "basic"
    PREMIUM = "premium"


class User:

    def __init__(self):
        self.defaults = {
            "id": string_utils.randID(),
            "ip_addresses": [request.remote_addr],
            "acct_active": True,
            "date_created": string_utils.nowDatetimeUTC(),
            "last_login": string_utils.nowDatetimeUTC(),
            "first_name": "",
            "last_name": "",
            "email": "",
            "plan": Plan.BASIC.value,  # Default to "basic"
            "refresh_token": None
        }

    def get(self):
        token_data = jwt.decode(request.headers.get('accesstoken'), app.config['secret_key'])
        user = fetch_data({"id": token_data['user_id']}, USERS_DATABASE)
        if not user or len(user) == 0:
            user = {"_id": 0, "password": 0}
        if user:
            resp = string_utils.JsonResp(user, 200)
        else:
            resp = string_utils.JsonResp({"message": "User not found"}, 404)
        return resp

    def getAuth(self):
        access_token = request.headers.get("accesstoken")
        if access_token:
            try:
                decoded = jwt.decode(access_token, app.config["secret_key"])
                resp = string_utils.JsonResp(decoded, 200)
            except Exception as e:
                resp = string_utils.JsonResp({"message": str(e)}, 401)
        else:
            resp = string_utils.JsonResp({"message": "User not logged in"}, 401)

        return resp

    def login(self):
        resp = string_utils.JsonResp({"message": "Invalid user credentials"}, 403)

        try:
            data = json.loads(request.data)
            email = data["email"].lower()
            user = fetch_data({"email": email}, USERS_DATABASE)[0]

            if user and pbkdf2_sha256.verify(data["password"], user["password"]):
                # Ensure all values passed to token encoding are strings
                user_id = str(user["_id"])
                user_email = str(user["email"])
                user_plan = str(user["plan"])  # Convert plan to string if it's not already

                access_token = encodeAccessToken(user_id, user_email, user_plan)
                refresh_token = encodeRefreshToken(user_id, user_email, user_plan)

                # Convert ObjectId back for MongoDB query

                filter = {"_id": ObjectId(user["_id"])}

                data = {
                    "refresh_token": refresh_token,
                    "last_login": string_utils.nowDatetimeUTC()
                }
                update_data(data, USERS_DATABASE, filter, MONGODB_SET_OPERATION)

                resp = string_utils.JsonResp({
                    "id": user_id,
                    "email": user_email,
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "plan": user_plan,
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, 200)
        except JSONDecodeError:
            resp = string_utils.JsonResp({"message": "Invalid JSON format"}, 400)
        except Exception as e:
            resp = string_utils.JsonResp({"message": str(e)}, 500)

        return resp

    def logout(self):
        try:
            token_data = jwt.decode(request.headers.get("AccessToken"), app.config["secret_key"])
            filter = {"id": token_data["user_id"]}
            data = {
                {"refresh_token": ""}
            }
            update_data(data, USERS_DATABASE, filter, MONGODB_UNSET_OPERATION)
            resp = string_utils.JsonResp({"message": "User logged out"}, 200)
        except Exception as e:
            resp = string_utils.JsonResp({"message": str(e)}, 500)

        return resp

    def add(self):
        try:
            data = json.loads(request.data)

            expected_data = {
                "first_name": data.get('first_name'),
                "last_name": data.get('last_name'),
                "email": data.get('email', '').lower(),
                "password": data.get('password'),
                "plan": data.get('plan', Plan.BASIC.value)  # Defaults to "basic" if not specified
            }

            # Validate required fields
            for field in ['first_name', 'last_name', 'email', 'password']:
                if not expected_data[field]:
                    return string_utils.JsonResp({"message": f"{field.replace('_', ' ').capitalize()} is required"}, 400)

            # Validate the plan field to ensure it's either 'basic' or 'premium'
            if expected_data['plan'] not in [plan.value for plan in Plan]:
                return string_utils.JsonResp({"message": "Invalid plan type. Must be 'basic' or 'premium'"}, 400)

            # Merge the posted data with the default user attributes
            self.defaults.update(expected_data)
            user = self.defaults

            # Encrypt the password
            user["password"] = pbkdf2_sha256.encrypt(user["password"], rounds=20000, salt_size=16)

            # Check if a user with this email already exists
            existing_email = fetch_data({"email": user["email"]}, USERS_DATABASE)
            if existing_email:
                return string_utils.JsonResp({
                    "message": "There's already an account with this email address",
                    "error": "email_exists"
                }, 400)

            result = insert_data(user, USERS_DATABASE)

            # Log the user in (create and return tokens)
            access_token = encodeAccessToken(user["id"], user["email"], user["plan"])
            refresh_token = encodeRefreshToken(user["id"], user["email"], user["plan"])
            update_data({
                "refresh_token": refresh_token
            }, USERS_DATABASE, {"id": user["id"]}, MONGODB_SET_OPERATION)
            return string_utils.JsonResp({
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "plan": user["plan"],
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 201)
        except Exception:
            return string_utils.JsonResp({"message": "User could not be added"}, 400)
