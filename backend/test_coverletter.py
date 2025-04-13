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
    flask_app = create_app()
    return flask_app


@pytest.fixture
def client(test_app):
    """
    Fixture to provide a test client for the Flask application.
    Args:
        app: The Flask application instance provided by the app fixture.
    Yields:
        FlaskClient: The test client for making HTTP requests.
    """
    test_client = test_app.test_client()
    ctx = test_app.app_context()
    ctx.push()
    yield test_client
    ctx.pop()


@pytest.fixture
def user(test_client):
    """
    Fixture to create a test user and authenticate them.
    Args:
        client: The Flask test client provided by the client fixture.
    Yields:
        tuple: A tuple containing the user object and authentication header.
    """
    data = {"username": "testUser", "password": "test", "fullName": "fullName"}
    test_user = Users(
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
    test_user.save()
    response = test_client.post("/users/login", json=data)
    jdata = json.loads(response.data.decode("utf-8"))
    header = {"Authorization": "Bearer " + jdata["token"]}
    yield test_user, header
    test_user.delete()


def test_create_coverletter_success(test_client, test_user):
    """
    Test creating a cover letter with valid data and verify it's saved.
    """
    test_test_user, headers = test_user
    payload = {
        "content": "This is my test cover letter.",
        "title": "Job Application Cover Letter"
    }

    response = test_client.post("/coverletters", json=payload, headers=headers)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["message"] == "Cover letter created successfully"

    # Verify the cover letter was saved
    updated_test_user = test_user.objects(id=test_test_user.id).first()
    assert updated_test_user is not None
    assert len(updated_test_user.coverletters) == 1
    assert updated_test_user.coverletters[0]["content"] == payload["content"]
    assert updated_test_user.coverletters[0]["title"] == payload["title"]


def test_create_coverletter_missing_content(test_client, test_user):
    """
    Test creating a cover letter without the required 'content' field.
    """
    _, headers = test_user
    payload = {"title": "Missing Content"}

    response = test_client.post("/coverletters", json=payload, headers=headers)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Cover letter content is required"


def test_create_coverletter_empty_payload(test_client, test_user):
    """
    Test creating a cover letter with an empty JSON payload.
    """
    _, headers = test_user
    response = test_client.post("/coverletters", json={}, headers=headers)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Cover letter content is required"


def test_create_coverletter_long_content(test_client, test_user):
    """
    Test creating a cover letter with a very large content body.
    """
    _, headers = test_user
    long_content = "A" * 10000
    response = test_client.post("/coverletters", json={"content": long_content}, headers=headers)
    assert response.status_code == 201
    assert "message" in response.get_json()


def test_create_coverletter_special_characters(test_client, test_user):
    """
    Test creating a cover letter with special and Unicode characters.
    """
    _, headers = test_user
    content = "你好，世界! 💼✨"
    response = test_client.post("/coverletters", json={"content": content}, headers=headers)
    assert response.status_code == 201


def test_create_duplicate_title(test_client, test_user):
    """
    Test creating multiple cover letters with the same title.
    """
    test_test_user, headers = test_user
    payload = {"content": "CL 1", "title": "Duplicate Title"}
    test_client.post("/coverletters", json=payload, headers=headers)
    test_client.post("/coverletters", json=payload, headers=headers)
    updated_test_user = test_user.objects(id=test_test_user.id).first()
    assert len(updated_test_user.coverletters) == 2


def test_get_all_coverletters_empty(test_client, test_user):
    """
    Test getting all cover letters when test_user has none.
    """
    test_user, header = test_user
    test_user.coverletters = []
    test_user.save()

    response = test_client.get("/coverletters", headers=header)
    assert response.status_code == 200
    assert response.json["coverletters"] == []


def test_get_all_coverletters(test_client, test_user):
    """
    Gets all the coverletters for a test_user.
    """
    test_user, header = test_user
    test_user.coverletters = ["mock_cover_1", "mock_cover_2"]
    test_user.save()

    response = test_client.get("/coverletters", headers=header)
    assert response.status_code == 200
    assert response.json["coverletters"] == ["mock_cover_1", "mock_cover_2"]


def test_get_single_coverletter_success(test_client, test_user):
    """
    Gets a single coverletter for a test_user.
    """
    test_user, header = test_user
    test_user.coverletters = ["cover1", "cover2"]
    test_user.save()

    response = test_client.get("/coverletters/1", headers=header)
    assert response.status_code == 200
    assert response.json["coverletter"] == "cover2"


def test_get_single_coverletter_not_found(test_client, test_user):
    """
    Tests getting a single coverletter that does not exist.
    """
    test_user, header = test_user
    test_user.coverletters = ["only_one"]
    test_user.save()

    response = test_client.get("/coverletters/3", headers=header)
    assert response.status_code == 404
    assert "Cover letter not found" in response.json["error"]


def test_update_coverletter_success(test_client, test_user):
    """
    Tests updating a coverletter successfully.
    """
    test_user, header = test_user
    test_user.coverletters = [{"content": "old", "title": "Old Title"}]
    test_user.save()

    response = test_client.put(
        "/coverletters/0",
        headers=header,
        json={"content": "new", "title": "Updated Title"}
    )

    assert response.status_code == 200
    assert response.json["message"] == "Cover letter updated successfully"


def test_update_coverletter_empty_string(test_client, test_user):
    """
    Test updating a cover letter with empty content.
    """
    test_user, header = test_user
    test_user.coverletters = [{"content": "initial", "title": "Title"}]
    test_user.save()

    response = test_client.put("/coverletters/0", headers=header, json={"content": ""})
    assert response.status_code == 200


def test_update_coverletter_missing_content(test_client, test_user):
    """
    Tests updating a coverletter with missing content.
    """
    test_user, header = test_user
    test_user.coverletters = [{"content": "existing"}]
    test_user.save()

    response = test_client.put("/coverletters/0", headers=header, json={})
    assert response.status_code == 400
    assert "content is required" in response.json["error"]


def test_update_coverletter_out_of_range(test_client, test_user):
    """
    Tests updating a coverletter that is out of range.
    """
    test_user, header = test_user
    test_user.coverletters = [{"content": "only one"}]
    test_user.save()

    response = test_client.put("/coverletters/5", headers=header, json={"content": "test"})
    assert response.status_code == 404
    assert "not found" in response.json["error"]


def test_update_coverletter_negative_index(test_client, test_user):
    """
    Tests updating a coverletter using a negative index.
    """
    _, header = test_user
    response = test_client.put("/coverletters/-1", headers=header, json={"content": "new"})
    assert response.status_code == 404


def test_delete_coverletter_success(test_client, test_user):
    """
    Tests deleting a coverletter successfully.
    """
    test_user, header = test_user
    test_user.coverletters = ["cl1", "cl2"]
    test_user.save()

    response = test_client.delete("/coverletters/1", headers=header)
    assert response.status_code == 200
    assert response.json["message"] == "Cover letter deleted successfully"


def test_delete_coverletter_not_found(test_client, test_user):
    """
    Tests deleting a coverletter that does not exist.
    """
    test_user, header = test_user
    test_user.coverletters = ["only one"]
    test_user.save()

    response = test_client.delete("/coverletters/3", headers=header)
    assert response.status_code == 404
    assert "not found" in response.json["error"]


def test_delete_last_coverletter(test_client, test_user):
    """
    Test deleting the last remaining cover letter.
    """
    test_user, header = test_user
    test_user.coverletters = ["only"]
    test_user.save()

    response = test_client.delete("/coverletters/0", headers=header)
    assert response.status_code == 200
    updated_test_user = test_user.objects(id=test_user.id).first()
    assert updated_test_user.coverletters == []


def test_invalid_index_type(test_client, test_user):
    """
    Test passing a non-integer index to cover letter routes.
    """
    _, header = test_user
    response = test_client.get("/coverletters/abc", headers=header)
    assert response.status_code == 404


def test_script_injection_content(test_client, test_user):
    """
    Test injecting HTML/script content into a cover letter.
    """
    _, headers = test_user
    content = "<script>alert('XSS')</script>"
    response = test_client.post("/coverletters", json={"content": content}, headers=headers)
    assert response.status_code == 201
