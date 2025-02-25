"""
This module contains utility functions for the application.
"""

from flask import request, jsonify
from datetime import datetime
from models import Users


def get_token_from_header():
    headers = request.headers
    token = headers["Authorization"].split(" ")[1]
    return token


def get_userid_from_header():
    token = get_token_from_header()
    userid = token.split(".")[0]
    return userid


def delete_auth_token(token_to_delete, user_id):
    user = Users.objects(id=user_id).first()
    auth_tokens = []
    for token in user["authTokens"]:
        if token != token_to_delete:
            auth_tokens.append(token)
    user.update(authTokens=auth_tokens)


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
