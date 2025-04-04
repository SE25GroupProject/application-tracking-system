"""
This module defines the database models for the application.
"""

from db import db


# Define an EmbeddedDocument for the Profile structure
class Profile(db.EmbeddedDocument):
    profileName = db.StringField(unique=True)
    skills = db.ListField(db.StringField())  
    job_levels = db.ListField(db.StringField())  
    locations = db.ListField(db.StringField())  
    institution = db.StringField() 
    phone_number = db.StringField()  
    address = db.StringField() 

# Updated Users class
class Users(db.Document):
    id = db.IntField(primary_key=True)
    fullName = db.StringField() 
    username = db.StringField()
    password = db.StringField()
    authTokens = db.ListField()
    email = db.StringField()  
    applications = db.ListField()
    resumes = db.ListField(db.FileField())
    resumeFeedbacks = db.ListField()
    
    # Add a list of profiles
    profiles = db.EmbeddedDocumentListField(Profile)
    
    # Add a pointer to the default profile 
    default_profile = db.IntField(default=0) 

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
    return new_id + 1
