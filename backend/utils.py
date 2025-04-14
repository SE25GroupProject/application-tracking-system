"""
This module contains utility functions for the application.
"""

from functools import wraps
from datetime import datetime
from flask import request, jsonify
from models import Users


def get_token_from_header():
    """Gets the token from the request header."""
    headers = request.headers
    token = headers["Authorization"].split(" ")[1]
    return token


def get_userid_from_header():
    """Gets the user ID from the request header."""
    token = get_token_from_header()
    userid = token.split(".")[0]
    return userid


def delete_auth_token(token_to_delete, user_id):
    """Deletes the specified auth token from the user's authTokens list."""
    user = Users.objects(id=user_id).first()
    auth_tokens = []
    for token in user["authTokens"]:
        if token != token_to_delete:
            auth_tokens.append(token)
    user.update(authTokens=auth_tokens)


def authorized(f):
    """
    Decorator to enforce the request is from an authorized user.
    The User object is passed as the last positional argument to the route.
    """

    @wraps(f)
    def authorized_route(*args, **kwargs):
        try:
            userid = get_userid_from_header()
            user = Users.objects(id=id).first()
            assert user is not None

            token = get_token_from_header()
            valid_flag = False
            for tokens in user["authTokens"]:
                if tokens["token"] == token:
                    expiry = tokens["expiry"]
                    expiry_time_object = datetime.strptime(expiry, "%m/%d/%Y, %H:%M:%S")
                    if datetime.now() <= expiry_time_object:
                        valid_flag = True
                    else:
                        delete_auth_token(tokens["token"], userid)
                    break

            assert valid_flag
        except:
            return jsonify({"error": "Unauthorized"}), 401

        return f(*args, user, **kwargs)

    return authorized_route


def middleware(authorized_endpoints):
    """
    Checks for user authorization tokens and returns message

    :return: JSON object
    """

    def middleware_function():
        try:
            if request.method == "OPTIONS":
                return jsonify({"success": "OPTIONS"}), 200
            if request.path in authorized_endpoints:
                headers = request.headers
                try:
                    token = headers["Authorization"].split(" ")[1]
                except:
                    return jsonify({"error": "Unauthorized"}), 401
                userid = token.split(".")[0]
                user = Users.objects(id=userid).first()

                if user is None:
                    return jsonify({"error": "Unauthorized"}), 401

                expiry_flag = False
                for tokens in user["authTokens"]:
                    if tokens["token"] == token:
                        expiry = tokens["expiry"]
                        expiry_time_object = datetime.strptime(
                            expiry, "%m/%d/%Y, %H:%M:%S"
                        )
                        if datetime.now() <= expiry_time_object:
                            expiry_flag = True
                        else:
                            delete_auth_token(tokens, userid)
                        break

                if not expiry_flag:
                    return jsonify({"error": "Unauthorized"}), 401

        except:
            return jsonify({"error": "Internal server error"}), 500

    return middleware_function
