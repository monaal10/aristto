from datetime import datetime, timedelta
from enum import Enum
from json import JSONDecodeError

from flask import current_app as app, request, make_response
from flask import json
import jwt
from passlib.hash import pbkdf2_sha256

from main.classes.mongodb import fetch_data, update_data, insert_data
from main.utils import string_utils
from main.utils.auth_utils import encodeAccessToken, encodeRefreshToken
from main.utils.constants import USERS_DATABASE, MONGODB_SET_OPERATION, MONGODB_UNSET_OPERATION, CLIENT_URL
from bson import ObjectId

import logging

from main.utils.email_utils import SESEmailSender

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
class Plan(Enum):
    FREE = "free"
    PRO = "pro"


class User:

    def __init__(self):
        self.defaults = {
            "user_id": string_utils.randID(),
            "ip_addresses": [request.remote_addr],
            "acct_active": True,
            "date_created": string_utils.nowDatetimeUTC(),
            "last_login": string_utils.nowDatetimeUTC(),
            "first_name": "",
            "last_name": "",
            "email": "",
            "plan": Plan.FREE.value,  # Default to "free"
            "refresh_token": None,
            "stripe_customer_id": None,
            "stripe_subscription_id": None,
            "subscription_status": None,
        }

    def get(self):
        try:
            # Get user data from the decoded token stored in request
            user = fetch_data({"user_id": request.user["user_id"]}, USERS_DATABASE)
            if not user or len(user) == 0:
                return string_utils.JsonResp({"message": "User not found"}, 404)

            if user and len(user) > 0:
                # Remove sensitive fields
                user_data = user[0]
                if "_id" in user_data: del user_data["_id"]
                if "password" in user_data: del user_data["password"]
                resp = string_utils.JsonResp(user_data, 200)
            else:
                resp = string_utils.JsonResp({"message": "User not found"}, 404)

        except Exception as e:
            resp = string_utils.JsonResp({"message": str(e)}, 401)
        return resp

    def getAuth(self):
        access_token = request.cookies.get('access_token')  # Make sure header name matches
        if not access_token:
            return string_utils.JsonResp({"message": "No access token provided"}, 401)

        try:
            decoded = jwt.decode(access_token, app.config["secret_key"], algorithms=["HS256"])
            return string_utils.JsonResp(decoded, 200)
        except jwt.ExpiredSignatureError:
            return string_utils.JsonResp({"message": "Token has expired"}, 401)
        except jwt.InvalidTokenError:
            return string_utils.JsonResp({"message": "Token is invalid"}, 401)
        except Exception as e:
            print(f"Auth error: {str(e)}")  # Add logging for debugging
            return string_utils.JsonResp({"message": str(e)}, 401)

    def login(self):
        try:
            data = json.loads(request.data)
            email = data["email"].lower()
            user = fetch_data({"email": email}, USERS_DATABASE)[0]

            if user and pbkdf2_sha256.verify(data["password"], user["password"]):
                user_id = str(user["user_id"])
                user_email = str(user["email"])
                user_plan = str(user["plan"])

                access_token = encodeAccessToken(user_id, user_email, user_plan)
                refresh_token = encodeRefreshToken(user_id, user_email, user_plan)

                # Update user in database
                filter = {"user_id": user["user_id"]}
                update_data({
                    "refresh_token": refresh_token,
                    "last_login": string_utils.nowDatetimeUTC()
                }, USERS_DATABASE, filter, MONGODB_SET_OPERATION)

                response_data = {
                    "user_id": user_id,
                    "email": user_email,
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "plan": user_plan,
                }

                response = make_response(string_utils.JsonResp(response_data, 200))

                response.set_cookie(
                    'access_token',
                    access_token,
                    httponly=True,
                    secure=True,  # True in production (HTTPS)
                    samesite='Strict',  # Strict in production
                    max_age=900,  # 15 minutes
                    path='/'
                )

                # Refresh token cookie
                response.set_cookie(
                    'refresh_token',
                    refresh_token,
                    httponly=True,
                    secure=True,  # True in production (HTTPS)
                    samesite='Strict',  # Strict in production
                    max_age=2592000,  # 30 days
                    path='/'
                )

                return response

            return string_utils.JsonResp({"message": "Invalid user credentials"}, 403)
        except Exception as e:
            return string_utils.JsonResp({"message": str(e)}, 500)

    def logout(self):
        try:
            # Create response with cleared cookies
            response = make_response(string_utils.JsonResp({"message": "User logged out"}, 200))
            response.delete_cookie('access_token', path='/')
            response.delete_cookie('refresh_token', path='/')

            return response

        except Exception as e:
            return string_utils.JsonResp({"message": str(e)}, 500)

    def add(self):
        try:
            data = json.loads(request.data)

            expected_data = {
                "first_name": data.get('first_name'),
                "last_name": data.get('last_name'),
                "email": data.get('email', '').lower(),
                "password": data.get('password'),
                "plan": data.get('plan', Plan.FREE.value)  # Defaults to "basic" if not specified
            }

            # Validate required fields
            for field in ['first_name', 'last_name', 'email', 'password']:
                if not expected_data[field]:
                    return string_utils.JsonResp({"message": f"{field.replace('_', ' ').capitalize()} is required"}, 400)

            # Merge the posted data with the default user attributes
            self.defaults.update(expected_data)
            user = self.defaults

            # Encrypt the password
            user["password"] = pbkdf2_sha256.encrypt(user["password"], rounds=20000, salt_size=16)

            # Check if a user with this email already exists
            existing_email = fetch_data({"email": user["email"]}, USERS_DATABASE)
            if existing_email and len(existing_email) > 0:
                return string_utils.JsonResp({
                    "message": "There's already an account with this email address",
                    "error": "email_exists"
                }, 400)

            insert_data(user, USERS_DATABASE)

            # Log the user in (create and return tokens)
            access_token = encodeAccessToken(user["user_id"], user["email"], user["plan"])
            refresh_token = encodeRefreshToken(user["user_id"], user["email"], user["plan"])
            update_data({
                "refresh_token": refresh_token
            }, USERS_DATABASE, {"user_id": user["user_id"]}, MONGODB_SET_OPERATION)
            logger.info(user["user_id"])
            return string_utils.JsonResp({
                "user_id": user["user_id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "plan": user["plan"],
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 201)
        except Exception:
            return string_utils.JsonResp({"message": "User could not be added"}, 400)

    def refresh(self):
        try:
            data = json.loads(request.data)
            refresh_token = data.get('refresh_token')

            if not refresh_token:
                return string_utils.JsonResp({"message": "Refresh token is required"}, 400)

            # Verify the refresh token exists in the database
            users = fetch_data({"refresh_token": refresh_token}, USERS_DATABASE)
            if not users or len(users) == 0:
                return string_utils.JsonResp({"message": "Invalid refresh token"}, 401)

            user = users[0]

            try:
                # Decode the refresh token
                decoded = jwt.decode(refresh_token, app.config["secret_key"], algorithms=["HS256"])

                # Generate new access token
                new_access_token = encodeAccessToken(
                    str(user["_id"]),  # Ensure we convert ObjectId to string
                    user["email"],
                    user["plan"]
                )

                return string_utils.JsonResp({
                    "new_access_token": new_access_token,
                    "message": "Token refreshed successfully"
                }, 200)

            except jwt.ExpiredSignatureError:
                # Remove expired refresh token from database
                update_data(
                    {"refresh_token": ""},
                    USERS_DATABASE,
                    {"refresh_token": refresh_token},
                    MONGODB_UNSET_OPERATION
                )
                return string_utils.JsonResp({"message": "Refresh token has expired"}, 401)

            except jwt.InvalidTokenError:
                return string_utils.JsonResp({"message": "Invalid refresh token format"}, 401)

        except JSONDecodeError:
            return string_utils.JsonResp({"message": "Invalid JSON format"}, 400)
        except Exception as e:
            # Log the actual error for debugging
            print(f"Refresh token error: {str(e)}")
            return string_utils.JsonResp({"message": "Internal server error", "error": str(e)}, 500)


    def update_subscription(self):
        try:
            data = json.loads(request.data)
            user_id = data.get('user_id')
            stripe_customer_id = data.get('stripe_customer_id')
            stripe_subscription_id = data.get('stripe_subscription_id')
            subscription_status = data.get('subscription_status')
            plan = data.get('plan')
            update_data({
            "stripe_customer_id": stripe_customer_id,
            "stripe_subscription_id" : stripe_subscription_id,
            "subscription_status": subscription_status,
            "plan": plan
        }, USERS_DATABASE, {"user_id": user_id}, MONGODB_SET_OPERATION)
            return string_utils.JsonResp({"Plan updated"}, 201)

        except Exception as e:
            raise f"Failed to update subscription {e}"

    def request_password_reset(self):
        try:
            data = json.loads(request.data)
            email = data.get('email', '').lower()

            # Check if user exists
            user = fetch_data({"email": email}, USERS_DATABASE)
            if not user:
                return string_utils.JsonResp({"message": "If an account exists with this email, you will receive a password reset link"}, 200)

            user = user[0]
            user_id = str(user["user_id"])

            # Generate reset token
            reset_token = jwt.encode({
                'user_id': user_id,
                'email': email,
                'exp': datetime.utcnow() + timedelta(hours=1)
            }, app.config['secret_key'], algorithm='HS256')

            # Store reset token in database
            update_data({
                "reset_token": reset_token,
                "reset_token_expires": datetime.utcnow() + timedelta(hours=1)
            }, USERS_DATABASE, {"user_id": user_id}, MONGODB_SET_OPERATION)

            # Send reset email using SES
            reset_url = f"{CLIENT_URL}/reset-password/{reset_token}"
            email_sender = SESEmailSender()
            email_sender.send_reset_password_email(email, reset_url)

            return string_utils.JsonResp({
                "message": "If an account exists with this email, you will receive a password reset link"
            }, 200)

        except Exception as e:
            logger.error(f"Password reset request error: {str(e)}")
            return string_utils.JsonResp({"message": "Failed to process password reset request"}, 500)

    def reset_password(self):
        try:
            data = json.loads(request.data)
            token = data.get('token')
            new_password = data.get('newPassword')

            if not token or not new_password:
                return string_utils.JsonResp({"message": "Invalid request"}, 400)

            try:
                # Verify token
                payload = jwt.decode(token, app.config['secret_key'], algorithms=['HS256'])
                user_id = payload['user_id']
                email = payload['email']

                # Check if token is valid in database
                user = fetch_data({
                    "user_id": user_id,
                    "reset_token": token,
                    "reset_token_expires": {"$gt": datetime.utcnow()}
                }, USERS_DATABASE)

                if not user:
                    return string_utils.JsonResp({"message": "Invalid or expired reset token"}, 400)

                # Update password
                hashed_password = pbkdf2_sha256.encrypt(new_password, rounds=20000, salt_size=16)
                update_data({
                    "password": hashed_password,
                    "reset_token": "",
                    "reset_token_expires": None
                }, USERS_DATABASE, {"user_id": user_id}, MONGODB_SET_OPERATION)

                return string_utils.JsonResp({"message": "Password reset successfully"}, 200)

            except jwt.ExpiredSignatureError:
                return string_utils.JsonResp({"message": "Reset token has expired"}, 400)
            except jwt.InvalidTokenError:
                return string_utils.JsonResp({"message": "Invalid reset token"}, 400)

        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return string_utils.JsonResp({"message": "Failed to reset password"}, 500)

