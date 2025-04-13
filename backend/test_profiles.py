"""
Test module for profile-related endpoints (starting from Test 42)
"""

import hashlib

import pytest
import json
from app import create_app
from models import Users, Profile


@pytest.fixture()
def app():
    """
    Fixture to create a test instance of the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = create_app()
    return app


@pytest.fixture
def client(app):
    """
    Fixture to provide a test client for the Flask application.

    Args:
        app: The Flask application instance provided by the app fixture.

    Yields:
        FlaskClient: The test client for making HTTP requests.
    """
    client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    yield client
    ctx.pop()


@pytest.fixture
def user(client):
    """
    Fixture to create a test user and authenticate them.

    Args:
        client: The Flask test client provided by the client fixture.

    Yields:
        tuple: A tuple containing the user object and authentication header.
    """
    data = {"username": "testUser", "password": "test", "fullName": "fullName"}
    user = Users(
        id=1,
        fullName=data["fullName"],
        username=data["username"],
        password=hashlib.md5(data["password"].encode()).hexdigest(),
        authTokens=[],
        email="",
        applications=[],
        resumes=[],
        coverletters=[],
        resumeFeedbacks=[],
        profiles=[],
        default_profile=0
    )
    user.save()
    rv = client.post("/users/login", json=data)
    jdata = json.loads(rv.data.decode("utf-8"))
    header = {"Authorization": "Bearer " + jdata["token"]}
    yield user, header
    user.delete()


# Test 42: Get Default Profile (No Profiles)
def test_get_profile_no_profiles(client, user):
    """
    Test retrieving the default profile when no profiles exist.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    rv = client.get("/getProfile", headers=header)
    assert rv.status_code == 404
    assert json.loads(rv.data) == {"error": "No profile available"}


# Test 43: Get Default Profile
def test_get_default_profile(client, user):
    """
    Test retrieving the default profile with valid data.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    user.email = "test@example.com"
    profile = Profile(profileName="Test Profile", skills=["Python"])
    user.profiles.append(profile)
    user.save()
    rv = client.get("/getProfile", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["profileName"] == "Test Profile"
    assert data["skills"] == ["Python"]
    assert data["email"] == "test@example.com"
    assert data["profileid"] == 0


# Test 44: Get Profile by ID
def test_get_profile_by_id(client, user):
    """
    Test retrieving a profile by its ID.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    profile1 = Profile(profileName="Profile 1")
    profile2 = Profile(profileName="Profile 2")
    user.profiles.extend([profile1, profile2])
    user.save()
    rv = client.get("/getProfile/1", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["profileName"] == "Profile 2"
    assert data["profileid"] == 1


# Test 45: Get Profile with Invalid ID
def test_get_profile_invalid_id(client, user):
    """
    Test retrieving a profile with an invalid ID.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    profile = Profile(profileName="Test Profile")
    user.profiles.append(profile)
    user.save()
    rv = client.get("/getProfile/999", headers=header)
    assert rv.status_code == 400
    assert json.loads(rv.data) == {"error": "Invalid profile ID"}


# Test 46: Update Default Profile
def test_update_default_profile(client, user):
    """
    Test updating the default profile.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    profile = Profile(profileName="Initial Profile")
    user.profiles.append(profile)
    user.save()
    update_data = {"profileName": "Updated Profile", "skills": ["Java"]}
    rv = client.post("/updateProfile", headers=header, json=update_data)
    assert rv.status_code == 200
    updated_user = Users.objects(id=user.id).first()
    assert updated_user.profiles[0].profileName == "Updated Profile"
    assert updated_user.profiles[0].skills == ["Java"]


# Test 47: Update Profile by ID
def test_update_profile_by_id(client, user):
    """
    Test updating a profile by its ID.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    profile1 = Profile(profileName="Profile 1")
    profile2 = Profile(profileName="Profile 2")
    user.profiles.extend([profile1, profile2])
    user.save()
    update_data = {"profileName": "Updated Profile 2"}
    rv = client.post("/updateProfile/1", headers=header, json=update_data)
    assert rv.status_code == 200
    updated_user = Users.objects(id=user.id).first()
    assert updated_user.profiles[1].profileName == "Updated Profile 2"


# Test 48: Update Profile with Invalid Field
def test_update_profile_invalid_field(client, user):
    """
    Test updating a profile with an invalid field.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    profile = Profile(profileName="Test Profile")
    user.profiles.append(profile)
    user.save()
    update_data = {"invalid_field": "value"}
    rv = client.post("/updateProfile", headers=header, json=update_data)
    assert rv.status_code == 400
    assert json.loads(rv.data) == {"error": "Invalid field: invalid_field"}


# Test 49: Update Profile with Invalid ID
def test_update_profile_invalid_id(client, user):
    """
    Test updating a profile with an invalid ID.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    profile = Profile(profileName="Test Profile")
    user.profiles.append(profile)
    user.save()
    update_data = {"profileName": "Updated"}
    rv = client.post("/updateProfile/999", headers=header, json=update_data)
    assert rv.status_code == 400
    assert json.loads(rv.data) == {"error": "Invalid profile ID"}


# Test 50: Update Non-existent Default Profile
def test_update_create_default_profile(client, user):
    """
    Test updating (creating) a default profile when none exists.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    update_data = {"profileName": "New Profile", "skills": ["Python"]}
    rv = client.post("/updateProfile", headers=header, json=update_data)
    assert rv.status_code == 200
    updated_user = Users.objects(id=user.id).first()
    assert len(updated_user.profiles) == 1
    assert updated_user.profiles[0].profileName == "New Profile"


# Test 51: Create Profile
def test_create_profile(client, user):
    """
    Test creating a new profile.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    profile_data = {"profileName": "New Profile", "skills": ["Java"]}
    rv = client.post("/createProfile", headers=header, json=profile_data)
    assert rv.status_code == 201
    data = json.loads(rv.data)
    assert data["message"] == "Profile created successfully"
    assert data["profileid"] == 0
    updated_user = Users.objects(id=user.id).first()
    assert updated_user.profiles[0].profileName == "New Profile"


# Test 52: Create Profile with Invalid Field
def test_create_profile_invalid_field(client, user):
    """
    Test creating a profile with an invalid field.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    profile_data = {"invalid_field": "value"}
    rv = client.post("/createProfile", headers=header, json=profile_data)
    assert rv.status_code == 400
    assert json.loads(rv.data) == {"error": "Invalid field: invalid_field"}


# Test 53: Set Default Profile
def test_set_default_profile(client, user):
    """
    Test setting a profile as the default.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    profile1 = Profile(profileName="Profile 1")
    profile2 = Profile(profileName="Profile 2")
    user.profiles.extend([profile1, profile2])
    user.save()
    rv = client.post("/setDefaultProfile/1", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["message"] == "Default profile updated successfully"
    assert data["default_profile"] == 1
    updated_user = Users.objects(id=user.id).first()
    assert updated_user.default_profile == 1


# Test 54: Set Default Profile with Invalid ID
def test_set_default_profile_invalid_id(client, user):
    """
    Test setting a default profile with an invalid ID.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    profile = Profile(profileName="Test Profile")
    user.profiles.append(profile)
    user.save()
    rv = client.post("/setDefaultProfile/999", headers=header)
    assert rv.status_code == 400
    assert json.loads(rv.data) == {"error": "Invalid profile ID"}


# Test 55: Get Profile List (Empty)
def test_get_profile_list_empty(client, user):
    """
    Test retrieving the profile list when no profiles exist.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    rv = client.get("/getProfileList", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["profiles"] == []
    assert data["default_profile"] == 0


# Test 56: Get Profile List
def test_get_profile_list(client, user):
    """
    Test retrieving the list of profiles.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    profile1 = Profile(profileName="Profile 1")
    profile2 = Profile(profileName="Profile 2")
    user.profiles.extend([profile1, profile2])
    user.default_profile = 1
    user.save()
    rv = client.get("/getProfileList", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data["profiles"]) == 2
    assert data["profiles"][0]["profileName"] == "Profile 1"
    assert data["profiles"][0]["isDefault"] == False
    assert data["profiles"][1]["profileName"] == "Profile 2"
    assert data["profiles"][1]["isDefault"] == True
    assert data["default_profile"] == 1


# Test 57: Update Profile with User Field
def test_update_profile_user_field(client, user):
    """
    Test updating a user field (email) through the profile update endpoint.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    profile = Profile(profileName="Test Profile")
    user.profiles.append(profile)
    user.save()
    update_data = {"email": "new@example.com"}
    rv = client.post("/updateProfile", headers=header, json=update_data)
    assert rv.status_code == 200
    updated_user = Users.objects(id=user.id).first()
    assert updated_user.email == "new@example.com"


# Test 58: Create Multiple Profiles
def test_create_multiple_profiles(client, user):
    """
    Test creating multiple profiles for a user.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    profile_data1 = {"profileName": "Profile 1", "skills": ["Python"]}
    profile_data2 = {"profileName": "Profile 2", "skills": ["Java"]}
    rv1 = client.post("/createProfile", headers=header, json=profile_data1)
    rv2 = client.post("/createProfile", headers=header, json=profile_data2)
    assert rv1.status_code == 201
    assert rv2.status_code == 201
    data1 = json.loads(rv1.data)
    data2 = json.loads(rv2.data)
    assert data1["profileid"] == 0
    assert data2["profileid"] == 1
    updated_user = Users.objects(id=user.id).first()
    assert len(updated_user.profiles) == 2
    assert updated_user.profiles[0].profileName == "Profile 1"
    assert updated_user.profiles[1].profileName == "Profile 2"
