"""
This module defines the database models for the application.
"""
# pylint: disable=no-member

from mongoengine import EmbeddedDocument, StringField
from mongoengine import ListField, FileField, IntField, EmbeddedDocumentListField, Document

# Define an EmbeddedDocument for the Profile structure
class Profile(EmbeddedDocument):
    """This class represents a user profile."""
    profileName = StringField(unique=True)
    skills = ListField(StringField())
    job_levels = ListField(StringField())
    locations = ListField(StringField())
    institution = StringField()
    phone_number = StringField()
    address = StringField()

# Updated Users class
class Users(Document):
    """This class represents a user in the application."""
    id = IntField(primary_key=True)
    fullName = StringField()
    username = StringField()
    password = StringField()
    authTokens = ListField()
    email = StringField()
    applications = ListField()
    resumes = ListField(FileField())
    coverletters = ListField(FileField())
    resumeFeedbacks = ListField()

    # Add a list of profiles
    profiles = EmbeddedDocumentListField(Profile)

    # Add a pointer to the default profile
    default_profile = IntField(default=0)

    def to_json(self, *args, **kwargs):
        """Convert the user object to JSON format."""
        return {"id": self.id, "fullName": self.fullName, "username": self.username}

def get_new_user_id():
    """Generate a new user ID by finding the maximum existing ID and adding one."""
    user_objects = Users.objects()
    if len(user_objects) == 0:
        return 1

    new_id = max(u["id"] for u in user_objects)
    return new_id + 1


def get_new_application_id(user_id):
    """Generate a new application ID for a user"""
    user = Users.objects(id=user_id).first()

    if len(user["applications"]) == 0:
        return 1

    new_id = max(a["id"] for a in user["applications"])
    return new_id + 1
