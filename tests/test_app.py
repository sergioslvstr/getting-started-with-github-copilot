import pytest
from fastapi.testclient import TestClient

import src.app as app_module


ACTIVITY_NAME = "Chess Club"
EXISTING_EMAIL = "student@mergington.edu"
NEW_EMAIL = "newstudent@mergington.edu"


@pytest.fixture
def client(monkeypatch):
    activities = {
        ACTIVITY_NAME: {
            "description": "Learn to play chess",
            "schedule": "Fridays at 3:30 PM",
            "max_participants": 4,
            "participants": [EXISTING_EMAIL],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return TestClient(app_module.app)


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()[ACTIVITY_NAME]["participants"] == [EXISTING_EMAIL]
    assert response.json()[ACTIVITY_NAME]["max_participants"] == 4


def test_signup_adds_participant(client):
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": NEW_EMAIL},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {NEW_EMAIL} for {ACTIVITY_NAME}"
    }
    assert NEW_EMAIL in client.get("/activities").json()[ACTIVITY_NAME]["participants"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": EXISTING_EMAIL},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": NEW_EMAIL},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant(client):
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": EXISTING_EMAIL},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {EXISTING_EMAIL} from {ACTIVITY_NAME}"
    }
    assert client.get("/activities").json()[ACTIVITY_NAME]["participants"] == []


def test_remove_rejects_unregistered_participant(client):
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": NEW_EMAIL},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_remove_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": NEW_EMAIL},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"