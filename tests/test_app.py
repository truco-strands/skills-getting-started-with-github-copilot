"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0


def test_signup_for_activity():
    """Test signing up for an activity"""
    # First, get initial participant count
    response = client.get("/activities")
    activities = response.json()
    chess_club = activities["Chess Club"]
    initial_count = len(chess_club["participants"])
    
    # Sign up a new participant
    test_email = "test@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={test_email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert test_email in data["message"]
    
    # Verify participant was added
    response = client.get("/activities")
    activities = response.json()
    chess_club = activities["Chess Club"]
    assert len(chess_club["participants"]) == initial_count + 1
    assert test_email in chess_club["participants"]


def test_signup_duplicate():
    """Test that duplicate signups are prevented"""
    test_email = "duplicate@mergington.edu"
    
    # First signup should succeed
    response = client.post(f"/activities/Chess Club/signup?email={test_email}")
    assert response.status_code == 200
    
    # Second signup should fail
    response = client.post(f"/activities/Chess Club/signup?email={test_email}")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"].lower()


def test_unregister_from_activity():
    """Test unregistering from an activity"""
    test_email = "unregister@mergington.edu"
    
    # First sign up
    response = client.post(f"/activities/Chess Club/signup?email={test_email}")
    assert response.status_code == 200
    
    # Then unregister
    response = client.delete(f"/activities/Chess Club/unregister?email={test_email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert test_email in data["message"]
    
    # Verify participant was removed
    response = client.get("/activities")
    activities = response.json()
    chess_club = activities["Chess Club"]
    assert test_email not in chess_club["participants"]


def test_unregister_not_registered():
    """Test unregistering someone who isn't registered"""
    test_email = "notregistered@mergington.edu"
    
    response = client.delete(f"/activities/Chess Club/unregister?email={test_email}")
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"].lower()


def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.delete("/activities/NonExistent/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_root_redirect():
    """Test that root redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers["location"]