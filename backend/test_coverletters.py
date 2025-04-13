"""
Test Module For Coverletters
"""

import hashlib

import json
from io import BytesIO
import pytest
from app import create_app
from models import Users


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


def test_coverletter_upload_fail(client, mocker, user):
    """
    Test uploading a text file as a coverletter, expecting failure.
    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    user, header = user
    user.applications = []
    user.coverletters = []
    user.save()
    data = dict(
        file=(BytesIO(b"testing coverletter"), "coverletter.txt"),
    )
    rv = client.post(
        "/coverletter", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 500

def test_coverletter_upload_pass(client, mocker, user):
    """
    Test uploading a PDF file as a coverletter, expecting success.
    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    user, header = user
    user.applications = []
    user.coverletters = []
    user.save()
    data = dict(
        file=(BytesIO(b"testing coverletter"), "data/coverletter.pdf"),
    )
    rv = client.post(
        "/coverletter", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 201

def test_get_all_coverletters(client, user):
    """Gets all the coverletters for a user."""
    user, header = user
    user.coverletters = ["mock_cover_1", "mock_cover_2"]
    user.save()

    response = client.get("/coverletters", headers=header)
    assert response.status_code == 200
    assert response.json["coverletters"] == ["mock_cover_1", "mock_cover_2"]

def test_get_single_coverletter_success(client, user):
    """Gets a single coverletter for a user."""
    user, header = user
    user.coverletters = ["cover1", "cover2"]
    user.save()

    response = client.get("/coverletters/1", headers=header)
    assert response.status_code == 200
    assert response.json["coverletter"] == "cover2"

def test_get_single_coverletter_not_found(client, user):
    """Tests getting a single coverletter that does not exist."""
    user, header = user
    user.coverletters = ["only_one"]
    user.save()

    response = client.get("/coverletters/3", headers=header)
    assert response.status_code == 404
    assert "Cover letter not found" in response.json["error"]

def test_update_coverletter_success(client, user):
    """Tests updating a coverletter successfully."""
    user, header = user
    user.coverletters = [{"content": "old", "title": "Old Title"}]
    user.save()

    response = client.put(
        "/coverletters/0",
        headers=header,
        json={"content": "new", "title": "Updated Title"}
    )

    assert response.status_code == 200
    assert response.json["message"] == "Cover letter updated successfully"


def test_update_coverletter_missing_content(client, user):
    """Tests updating a coverletter with missing content."""
    user, header = user
    user.coverletters = [{"content": "existing"}]
    user.save()

    response = client.put("/coverletters/0", headers=header, json={})
    assert response.status_code == 400
    assert "content is required" in response.json["error"]


def test_update_coverletter_out_of_range(client, user):
    """Tests updating a coverletter that is out of range."""
    user, header = user
    user.coverletters = [{"content": "only one"}]
    user.save()

    response = client.put("/coverletters/5", headers=header, json={"content": "test"})
    assert response.status_code == 404
    assert "not found" in response.json["error"]


def test_delete_coverletter_success(client, user):
    """Tests deleting a coverletter successfully."""
    user, header = user
    user.coverletters = ["cl1", "cl2"]
    user.save()

    response = client.delete("/coverletters/1", headers=header)
    assert response.status_code == 200
    assert response.json["message"] == "Cover letter deleted successfully"


def test_delete_coverletter_not_found(client, user):
    """Tests deleting a coverletter that does not exist."""
    user, header = user
    user.coverletters = ["only one"]
    user.save()

    response = client.delete("/coverletters/3", headers=header)
    assert response.status_code == 404
    assert "not found" in response.json["error"]