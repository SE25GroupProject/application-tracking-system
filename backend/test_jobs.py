"""
Test module for search and recommendation endpoints (Tests 30-41)
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


# Test 30: Search with Valid Parameters
def test_search_route(client, mocker):
    """
    Test the search endpoint with valid parameters and mocked job data.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
    """
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    rv = client.get("/search?keywords=engineer&company=Scale AI&location=New York")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# Test 31: Search with No Results
def test_search_route_no_results(client, mocker):
    """
    Test the search endpoint when no results are returned.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
    """
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[]
    )
    rv = client.get("/search?keywords=nonexistent&company=Nonexistent&location=Nowhere")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) == 0


# Test 33: Recommendations with Valid Data
def test_get_recommendations_route(client, mocker, user):
    """
    Test the recommendations endpoint with valid user profile data.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    user, header = user
    user.profiles = [Profile(skills=["Python"], locations=["New York"])]
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# Test 34: Recommendations with No Skills
def test_get_recommendations_route_no_skills(client, user):
    """
    Test the recommendations endpoint when the user has no skills defined.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    user.profiles = [Profile(skills=[], locations=["New York"])]
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 400


# Test 35: Recommendations with No Locations
def test_get_recommendations_route_no_locations(client, user):
    """
    Test the recommendations endpoint when the user has no locations defined.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    user.profiles = [Profile(skills=[], locations=["New York"])]
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 400


# Test 36: Recommendations with Multiple Job Levels
def test_get_recommendations_route_multiple_job_levels(client, mocker, user):
    """
    Test the recommendations endpoint with multiple job levels in the profile.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    user, header = user
    user.profiles = user.profiles = [Profile(skills=["Python"], locations=["New York"], job_levels=["Entry-Level", "Director", "Intern"])]
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# Test 37: Search with Special Characters
def test_search_route_special_characters(client, mocker):
    """
    Test the search endpoint with special characters in query parameters.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
    """
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    rv = client.get("/search?keywords=engineer&company=Scale AI&location=New+York")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# Test 38: Recommendations with Multiple Skills
def test_get_recommendations_route_multiple_skills(client, mocker, user):
    """
    Test the recommendations endpoint with multiple skills in the profile.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    user, header = user
    user.profiles = [Profile(skills=["JavaScript", "Python", "Cooking"], locations=["New York"])]
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# Test 39: Recommendations with Multiple Locations
def test_get_recommendations_route_multiple_locations(client, mocker, user):
    """
    Test the recommendations endpoint with multiple locations in the profile.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    user, header = user
    user.profiles = [Profile(skills=["Python"], locations=["New York", "San Fransisco", "Raleigh"])]
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# Test 40: Search with Long Keywords
def test_search_route_long_keywords(client, mocker):
    """
    Test the search endpoint with excessively long keywords.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
    """
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    long_keywords = "engineer" * 50
    rv = client.get(f"/search?keywords={long_keywords}&company=Scale AI&location=New York")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# Test 41: Recommendations with Invalid User Data
def test_get_recommendations_route_no_user_data(client, mocker):
    """
    Test the recommendations endpoint with an invalid authentication token.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
    """
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    header = {"Authorization": "Bearer invalid"}
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 500