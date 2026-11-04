from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def isolated_activities(monkeypatch):
    activities = deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(isolated_activities):
    return TestClient(app_module.app)


def test_get_activities_returns_all_activities(client, isolated_activities):
    # Arrange
    expected_activities = isolated_activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, isolated_activities):
    # Arrange
    activity = "Art Club"
    email = "student@example.com"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in isolated_activities[activity]["participants"]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity = "Unknown Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": "student@example.com"})

    # Assert
    assert response.status_code == 404


def test_signup_rejects_duplicate_participant(client, isolated_activities):
    # Arrange
    activity = "Programming Class"
    email = isolated_activities[activity]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 409
    assert isolated_activities[activity]["participants"].count(email) == 1


def test_unregister_removes_participant(client, isolated_activities):
    # Arrange
    activity = "Art Club"
    email = "student@example.com"
    isolated_activities[activity]["participants"].append(email)

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in isolated_activities[activity]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity = "Unknown Club"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": "student@example.com"})

    # Assert
    assert response.status_code == 404


def test_unregister_returns_not_found_for_unregistered_participant(client, isolated_activities):
    # Arrange
    activity = "Art Club"
    email = "student@example.com"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert email not in isolated_activities[activity]["participants"]