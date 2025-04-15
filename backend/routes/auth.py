"""
This module contains the routes for user authentication.
"""
import hashlib
import uuid
import json
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, redirect, url_for, session
from authlib.common.security import generate_token
from models import Users, get_new_user_id, Profile
from config import config
from utils import get_token_from_header, get_userid_from_header

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/users/signupGoogle")
def signup_google():
    """Handles signing up with google"""
    auth_bp.oauth.register(
        name="google",
        client_id=config["GOOGLE_CLIENT_ID"],
        client_secret=config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url=config["CONF_URL"],
        client_kwargs={"scope": "openid email profile"},
        nonce="foobar",
    )
    redirect_uri = url_for("auth.authorized_google", _external=True)
    session["nonce"] = generate_token()
    return auth_bp.oauth.google.authorize_redirect(redirect_uri, nonce=session["nonce"])


@auth_bp.route("/users/signupGoogle/authorized")
def authorized_google():
    """Handles the callback from Google after authorization"""
    token = auth_bp.oauth.google.authorize_access_token()
    user = auth_bp.oauth.google.parse_id_token(token, nonce=session["nonce"])
    session["user"] = user

    user_exists = Users.objects(email=user["email"]).first()
    users_email = user["email"]
    full_name = user["given_name"] + " " + user["family_name"]

    if user["email_verified"]:
        if user_exists is None:
            # Create an empty default profile
            default_profile = Profile(
                profileName="default",
                skills=[],
                job_levels=[],
                locations=[],
                institution="",
                phone_number="",
                address=""
            )
            userSave = Users(
                id=get_new_user_id(),
                fullName=full_name,
                email=users_email,
                authTokens=[],
                applications=[],
                resumes=[],
                resumeFeedbacks=[],
                profiles=[default_profile],  # Initialize with one empty profile
                default_profile=0
            )
            userSave.save()
            unique_id = userSave["id"]
        else:
            unique_id = user_exists["id"]

        userSaved = Users.objects(email=user["email"]).first()
        expiry = datetime.now() + timedelta(days=1)
        expiry_str = expiry.strftime("%m/%d/%Y, %H:%M:%S")
        token_whole = str(unique_id) + "." + token["access_token"]
        auth_tokens_new = userSaved["authTokens"] + [
            {"token": token_whole, "expiry": expiry_str}
        ]
        userSaved.update(authTokens=auth_tokens_new)

        return redirect(
            f"http://127.0.0.1:3000/?token={token_whole}&expiry={expiry_str}&userId={unique_id}"
        )


@auth_bp.route("/users/signup", methods=["POST"])
def sign_up():
    """
    Creates a new user profile and adds the user to the database and returns the message

    :return: JSON object
    """
    try:
        data = json.loads(request.data)
        try:
            assert "username" in data
            assert "password" in data
            assert "fullName" in data
        except:
            return jsonify({"error": "Missing fields in input"}), 400

        username_exists = Users.objects(username=data["username"])
        if len(username_exists) != 0:
            return jsonify({"error": "Username already exists"}), 400

        password = data["password"]
        password_hash = hashlib.md5(password.encode())

        # Create an empty default profile
        default_profile = Profile(
            profileName=f"{data['fullName']}'s Default",
            skills=[],
            job_levels=[],
            locations=[],
            institution="",
            phone_number="",
            address=""
        )
        user = Users(
            id=get_new_user_id(),
            fullName=data["fullName"],
            username=data["username"],
            password=password_hash.hexdigest(),
            authTokens=[],
            applications=[],
            resumes=[],
            resumeFeedbacks=[],
            profiles=[default_profile],  # Initialize with one empty profile
            default_profile=0,
            email="",
            coverletters=[]
        )
        user.save()
        return jsonify(user.to_json()), 200
    except:
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/users/login", methods=["POST"])
def login():
    """
    Logs in the user and creates a new authorization token and stores in the database

    :return: JSON object with status and message
    """
    try:
        data = json.loads(request.data)
        try:
            assert "username" in data
            assert "password" in data
        except:
            return jsonify({"error": "Username or password missing"}), 400

        password_hash = hashlib.md5(data["password"].encode()).hexdigest()
        user = Users.objects(username=data["username"], password=password_hash).first()

        if user is None:
            return jsonify({"error": "Wrong username or password"}), 400

        token = str(user["id"]) + "." + str(uuid.uuid4())
        expiry = datetime.now() + timedelta(days=1)
        expiry_str = expiry.strftime("%m/%d/%Y, %H:%M:%S")
        auth_tokens_new = user["authTokens"] + [{"token": token, "expiry": expiry_str}]

        user.update(authTokens=auth_tokens_new)
        default_profile = user.profiles[user.default_profile] if user.profiles else None
        profileInfo = {
            "id": user.id,
            "fullName": user.fullName,
            "institution": default_profile.institution if default_profile else "",
            "skills": default_profile.skills if default_profile else [],
            "phone_number": default_profile.phone_number if default_profile else "",
            "address": default_profile.address if default_profile else "",
            "locations": default_profile.locations if default_profile else [],
            "job_levels": default_profile.job_levels if default_profile else [],
            "email": user.email,
        }

        return jsonify({"profile": profileInfo, "token": token, "expiry": expiry_str})

    except json.JSONDecodeError as err:
        print(err)
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/users/logout", methods=["POST"])
def logout():
    """
    Logs out the user and deletes the existing token from the database

    :return: JSON object with status and message
    """
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        auth_tokens = []
        incoming_token = get_token_from_header()
        for token in user["authTokens"]:
            if token["token"] != incoming_token:
                auth_tokens.append(token)
        user.update(authTokens=auth_tokens)

        return jsonify({"success": ""}), 200

    except:
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/protected-endpoint", methods=["GET"])
def protected_endpoint():
    """
    An endpoint that only logged in users can access
    """
    try:
        token = get_token_from_header()
        user_id = get_userid_from_header()
        user = Users.objects(id=user_id).first()
        if not user or not any(t["token"] == token for t in user["authTokens"]):
            return jsonify({"error": "Invalid or expired token"}), 401

        return jsonify({
            "message": "Protected data accessed",
            "user": {
                "id": user.id,
                "fullName": user.fullName,
                "email": user.email
            }
        }), 200
    except:
        return jsonify({"error": "Internal server error"}), 500
