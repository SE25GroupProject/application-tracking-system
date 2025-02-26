"""
This module defines the database models for the application.
"""

from db import db


class Users(db.Document):
    id = db.IntField(primary_key=True)
    fullName = db.StringField()
    username = db.StringField()
    password = db.StringField()
    authTokens = db.ListField()
    email = db.StringField()
    applications = db.ListField()
    resume = db.FileField()
    skills = db.ListField()
    job_levels = db.ListField()
    locations = db.ListField()
    institution = db.StringField()
    phone_number = db.StringField()
    address = db.StringField()

    def to_json(self):
        return {"id": self.id, "fullName": self.fullName, "username": self.username}


def get_new_user_id():
    user_objects = Users.objects()
    if len(user_objects) == 0:
        return 1

    new_id = max(u["id"] for u in user_objects)
    return new_id + 1


def get_new_application_id(user_id):
    user = Users.objects(id=user_id).first()

    if len(user["applications"]) == 0:
        return 1

    new_id = max(a["id"] for a in user["applications"])
    # String field so it is compatible with ids from career builder
    return str(int(new_id) + 1)
