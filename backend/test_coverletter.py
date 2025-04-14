"""""
Test Module For Coverletters
"""

import hashlib
import json
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
    response = client.post("/users/login", json=data)
    jdata = json.loads(response.data.decode("utf-8"))
    header = {"Authorization": "Bearer " + jdata["token"]}
    yield user, header
    user.delete()


def test_create_coverletter_success(client, user):
    """
    Test creating a cover letter with valid data and verify it's saved.
    """
    test_user, headers = user
    payload = {
        "content": "This is my test cover letter.",
        "title": "Job Application Cover Letter"
    }

    response = client.post("/coverletters", json=payload, headers=headers)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["message"] == "Cover letter created successfully"

    # Verify the cover letter was saved
    updated_user = Users.objects(id=test_user.id).first()
    assert updated_user is not None
    assert len(updated_user.coverletters) == 1
    assert updated_user.coverletters[0]["content"] == payload["content"]
    assert updated_user.coverletters[0]["title"] == payload["title"]


def test_create_coverletter_missing_content(client, user):
    """
    Test creating a cover letter without the required 'content' field.
    """
    _, headers = user
    payload = {"title": "Missing Content"}

    response = client.post("/coverletters", json=payload, headers=headers)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Cover letter content is required"


def test_create_coverletter_empty_payload(client, user):
    """
    Test creating a cover letter with an empty JSON payload.
    """
    _, headers = user
    response = client.post("/coverletters", json={}, headers=headers)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Cover letter content is required"


def test_create_coverletter_long_content(client, user):
    """
    Test creating a cover letter with a very large content body.
    """
    _, headers = user
    long_content = "A" * 10000
    response = client.post("/coverletters", json={"content": long_content}, headers=headers)
    assert response.status_code == 201
    assert "message" in response.get_json()


def test_create_coverletter_special_characters(client, user):
    """
    Test creating a cover letter with special and Unicode characters.
    """
    _, headers = user
    content = "你好，世界! 💼✨"
    response = client.post("/coverletters", json={"content": content}, headers=headers)
    assert response.status_code == 201


def test_create_duplicate_title(client, user):
    """
    Test creating multiple cover letters with the same title.
    """
    test_user, headers = user
    payload = {"content": "CL 1", "title": "Duplicate Title"}
    client.post("/coverletters", json=payload, headers=headers)
    client.post("/coverletters", json=payload, headers=headers)
    updated_user = Users.objects(id=test_user.id).first()
    assert len(updated_user.coverletters) == 2


def test_get_all_coverletters_empty(client, user):
    """
    Test getting all cover letters when user has none.
    """
    user, header = user
    user.coverletters = []
    user.save()

    response = client.get("/coverletters", headers=header)
    assert response.status_code == 200
    assert response.json["filenames"] == []


def test_get_all_coverletters(client, user):
    """
    Gets all the coverletters for a user.
    """
    user, header = user
    user.coverletters = [{"title": "mock_cover_1", "content": ""},{"title": "mock_cover_2", "content": ""}]
    user.save()

    response = client.get("/coverletters", headers=header)
    assert response.status_code == 200
    assert response.json["filenames"] == ["mock_cover_1", "mock_cover_2"]


def test_get_single_coverletter_success(client, user):
    """
    Gets a single coverletter for a user.
    """
    user, header = user
    user.coverletters = ["cover1", "cover2"]
    user.save()

    response = client.get("/coverletters/1", headers=header)
    assert response.status_code == 200
    assert response.json["coverletter"] == "cover2"


def test_get_single_coverletter_not_found(client, user):
    """
    Tests getting a single coverletter that does not exist.
    """
    user, header = user
    user.coverletters = ["only_one"]
    user.save()

    response = client.get("/coverletters/3", headers=header)
    assert response.status_code == 404
    assert "Cover letter not found" in response.json["error"]


def test_update_coverletter_success(client, user):
    """
    Tests updating a coverletter successfully.
    """
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


def test_update_coverletter_empty_string(client, user):
    """
    Test updating a cover letter with empty content.
    """
    user, header = user
    user.coverletters = [{"content": "initial", "title": "Title"}]
    user.save()

    response = client.put("/coverletters/0", headers=header, json={"content": ""})
    assert response.status_code == 200


def test_update_coverletter_missing_content(client, user):
    """
    Tests updating a coverletter with missing content.
    """
    user, header = user
    user.coverletters = [{"content": "existing"}]
    user.save()

    response = client.put("/coverletters/0", headers=header, json={})
    assert response.status_code == 400
    assert "content is required" in response.json["error"]


def test_update_coverletter_out_of_range(client, user):
    """
    Tests updating a coverletter that is out of range.
    """
    user, header = user
    user.coverletters = [{"content": "only one"}]
    user.save()

    response = client.put("/coverletters/5", headers=header, json={"content": "test"})
    assert response.status_code == 404
    assert "not found" in response.json["error"]


def test_update_coverletter_negative_index(client, user):
    """
    Tests updating a coverletter using a negative index.
    """
    _, header = user
    response = client.put("/coverletters/-1", headers=header, json={"content": "new"})
    assert response.status_code == 404


def test_delete_coverletter_success(client, user):
    """
    Tests deleting a coverletter successfully.
    """
    user, header = user
    user.coverletters = ["cl1", "cl2"]
    user.save()

    response = client.delete("/coverletters/1", headers=header)
    assert response.status_code == 200
    assert response.json["message"] == "Cover letter deleted successfully"


def test_delete_coverletter_not_found(client, user):
    """
    Tests deleting a coverletter that does not exist.
    """
    user, header = user
    user.coverletters = ["only one"]
    user.save()

    response = client.delete("/coverletters/3", headers=header)
    assert response.status_code == 404
    assert "not found" in response.json["error"]


def test_delete_last_coverletter(client, user):
    """
    Test deleting the last remaining cover letter.
    """
    user, header = user
    user.coverletters = ["only"]
    user.save()

    response = client.delete("/coverletters/0", headers=header)
    assert response.status_code == 200
    updated_user = Users.objects(id=user.id).first()
    assert updated_user.coverletters == []


def test_invalid_index_type(client, user):
    """
    Test passing a non-integer index to cover letter routes.
    """
    _, header = user
    response = client.get("/coverletters/abc", headers=header)
    assert response.status_code == 404


def test_script_injection_content(client, user):
    """
    Test injecting HTML/script content into a cover letter.
    """
    _, headers = user
    content = "<script>alert('XSS')</script>"
    response = client.post("/coverletters", json={"content": content}, headers=headers)
    assert response.status_code == 201
