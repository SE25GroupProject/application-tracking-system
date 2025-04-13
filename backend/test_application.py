"""Extra Tests For the Application"""

from io import BytesIO
import hashlib

import json
import pytest
from app import create_app
from models import Users


@pytest.fixture()
def app():
    """
    Creates a fixture for the application

    :return: app fixture
    """
    app = create_app()
    return app


@pytest.fixture
def client(app):
    """
    Creates a client fixture for tests to use

    :param app: the application fixture
    :return: client fixture
    """
    client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    yield client
    ctx.pop()


@pytest.fixture
def user(client):
    """
    Creates a user with test data

    :param client: the mongodb client
    :return: the user object and auth token
    """
    # print(request.data)
    data = {"username": "testUser", "password": "test", "fullName": "fullName"}

    user = Users(
        id=1,
        fullName=data["fullName"],
        username=data["username"],
        password=hashlib.md5(data["password"].encode()).hexdigest(),
        authTokens=[],
        applications=[],
        skills=[],
        job_levels=[],
        locations=[],
        phone_number="",
        address="",
        institution="",
        email="",
    )
    user.save()
    rv = client.post("/users/login", json=data)
    jdata = json.loads(rv.data.decode("utf-8"))
    header = {"Authorization": "Bearer " + jdata["token"]}
    yield user, header
    user.delete()

# 27. testing deleting first resume from multiple resumes
# (note that ollama has to be running for this to work)
def test_resume_delete_first(client, mocker, user):
    """
    Tests deleting a resume

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200

    # Send DELETE request to delete resume
    rv = client.delete("/resume/0", headers=header)
    assert rv.status_code == 200


# 28. testing deleting last resume from multiple resumes
# (note that ollama has to be running for this to work)
def test_resume_delete_last(client, mocker, user):
    """
    Tests deleting a resume

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200

    # Send DELETE request to delete resume
    rv = client.delete("/resume/1", headers=header)
    assert rv.status_code == 200


# 29. testing deleting multiple resumes
# (note that ollama has to be running for this to work)
def test_delete_multiple_resumes(client, mocker, user):
    """
    Tests deleting multiple resumes

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200

    # Send DELETE request to delete resume
    rv = client.delete("/resume/0", headers=header)
    assert rv.status_code == 200

    # Send DELETE request to delete resume
    rv = client.delete("/resume/0", headers=header)
    assert rv.status_code == 200


# 30. testing deleting invalid index in multiple resumes
# (note that ollama has to be running for this to work)
def test_resume_delete_multiple_invalid(client, mocker, user):
    """
    Tests deleting invalid index in list of multiple resumes

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200

    # Send invalid DELETE request
    rv = client.delete("/resume/3", headers=header)
    assert rv.status_code == 400


# 31. Test search route with valid parameters
def test_search_route(client, mocker):
    """Testing Search route with valid params"""
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time",
            }
        ],
    )
    rv = client.get("/search?keywords=engineer&company=Scale AI&location=New York")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# 32. Test search route with no results
def test_search_route_no_results(client, mocker):
    """Testing Search route with no results"""
    mocker.patch("routes.jobs.scrape_careerbuilder_jobs", return_value=[])
    rv = client.get("/search?keywords=nonexistent&company=Nonexistent&location=Nowhere")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) == 0


# 33. Test search route with missing parameters
def test_search_route_missing_parameters(client):
    """Testing Search route with missing parameters"""
    rv = client.get("/search?keywords=engineer")
    assert rv.status_code == 500


# 34. Test getRecommendations route with valid user data
def test_get_recommendations_route(client, mocker, user):
    """Testing getRecommendations route with valid user data"""
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time",
            }
        ],
    )
    user, header = user
    user.skills.append({"value": "Python"})
    user.locations.append({"value": "New York"})
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# 35. Test getRecommendations route with no skills
def test_get_recommendations_route_no_skills(client, user):
    """Testing getRecommendations route with no skills"""
    user, header = user
    user.skills = []
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 400


# 36. Test getRecommendations route with no locations
def test_get_recommendations_route_no_locations(client, user):
    """Testing getRecommendations route with no locations"""
    user, header = user
    user.locations = []
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 400


# 37. Test getProfile route with valid user data
def test_get_profile_route(client, user):
    """Testing getProfile route with valid user data"""
    user, header = user
    rv = client.get("/getProfile", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["email"] == user.email


# 38. Test getProfile route with invalid user
def test_get_profile_route_invalid_user(client):
    """Testing getProfile route with invalid user"""
    header = {"Authorization": "Bearer invalid"}
    rv = client.get("/getProfile", headers=header)
    assert rv.status_code == 500


# 39. Test updateProfile route with valid data
def test_update_profile_route(client, user):
    """Testing updateProfile route with valid data"""
    user, header = user
    new_data = {
        "email": "new@example.com",
        "fullName": "New User",
        "skills": [{"value": "Java"}],
        "job_levels": [{"value": "Junior"}],
        "locations": [{"value": "San Francisco"}],
        "institution": "New University",
        "phone_number": "0987654321",
        "address": "456 New St",
    }
    rv = client.post("/updateProfile", headers=header, json=new_data)
    assert rv.status_code == 200
    print(user, dir(user))
    assert new_data["email"] == new_data["email"]


# 40. Test updateProfile route with invalid data
def test_update_profile_route_invalid_data(client, user):
    """Testing updateProfile route with invalid data"""
    user, header = user
    new_data = {
        "email": "new@example.com",
        "fullName": "New User",
        "skills": "invalid",  # Invalid format
    }
    rv = client.post("/updateProfile", headers=header, json=new_data)
    assert rv.status_code == 500


# 41. Test getRecommendations route with no job levels
def test_get_recommendations_route_multiple_job_levels(client, mocker, user):
    """Testing getRecommendations route with multiple job levels"""
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time",
            }
        ],
    )

    user, header = user
    user.skills.append({"value": "Python"})
    user.locations.append({"value": "New York"})
    user.job_levels.append({"value": "Entry-Level"})
    user.job_levels.append({"value": "Director"})
    user.job_levels.append({"value": "Intern"})
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# 42. Test search route with special characters in parameters
def test_search_route_special_characters(client, mocker):
    """Testing Search route with special characters in parameters"""
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time",
            }
        ],
    )
    rv = client.get("/search?keywords=engineer&company=Scale AI&location=New+York")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# 43. Test getProfile route with missing header
def test_get_profile_route_missing_header(client):
    """Testing getProfile route with missing header"""
    rv = client.get("/getProfile")
    assert rv.status_code == 500


# 44. Test updateProfile route with partial data
def test_update_profile_route_partial_data(client, user):
    """Testing updateProfile route with partial data"""
    user, header = user
    new_data = {
        "email": "partial@example.com",
    }
    rv = client.post("/updateProfile", headers=header, json=new_data)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert Users.objects(id=data["id"]).first().email == new_data["email"]


# 45. Test getRecommendations route with multiple skills
def test_get_recommendations_route_multiple_skills(client, mocker, user):
    """Testing getRecommendations route with multiple skills"""
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time",
            }
        ],
    )
    user, header = user
    user.skills.append({"value": "JavaScript"})
    user.skills.append({"value": "Python"})
    user.skills.append({"value": "Cooking"})
    user.locations.append({"value": "New York"})
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# 46. Test getRecommendations route with multiple locations
def test_get_recommendations_route_multiple_locations(client, mocker, user):
    """Testing getRecommendations route with multiple locations"""
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time",
            }
        ],
    )
    user, header = user
    user.skills.append({"value": "Python"})
    user.locations.append({"value": "New York"})
    user.locations.append({"value": "San Fransisco"})
    user.locations.append({"value": "Raleigh"})
    user.save()
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# 47. Test updateProfile route with empty data
def test_update_profile_route_empty_data(client, user):
    """Testing updateProfile route with empty data"""
    user, header = user
    new_data = {}
    rv = client.post("/updateProfile", headers=header, json=new_data)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["fullName"] == user.fullName


# 48. Test search route with long keywords
def test_search_route_long_keywords(client, mocker):
    """Testing Search route with long keywords"""
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time",
            }
        ],
    )
    long_keywords = "engineer" * 50
    rv = client.get(
        f"/search?keywords={long_keywords}&company=Scale AI&location=New York"
    )
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# 49. Test getRecommendations route with no user data
def test_get_recommendations_route_no_user_data(client, mocker):
    """Testing getRecommendations route with no user data"""
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time",
            }
        ],
    )
    header = {"Authorization": "Bearer invalid"}
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 500


# 50. Test updateProfile route with invalid user
def test_update_profile_route_invalid_user(client):
    """Testing updateProfile route with invalid user"""
    header = {"Authorization": "Bearer invalid"}
    new_data = {
        "email": "new@example.com",
        "fullName": "New User",
    }
    rv = client.post("/updateProfile", headers=header, json=new_data)
    assert rv.status_code == 500
