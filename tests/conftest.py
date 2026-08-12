"""
Pytest configuration and shared fixtures for FastAPI app tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient instance for testing the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture
def activities_with_participants():
    """
    Fixture that provides a fresh copy of activities data for each test.
    This ensures test isolation - changes in one test don't affect others.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for tournament play",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Tennis Club": {
            "description": "Recreational tennis for all skill levels",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 8,
            "participants": []
        },
        "Drama Club": {
            "description": "Theater performances and acting workshops",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Art Club": {
            "description": "Painting, drawing, and creative projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Science Club": {
            "description": "Hands-on experiments and STEM projects",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": []
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": []
        }
    }


@pytest.fixture(autouse=True)
def reset_activities(activities_with_participants):
    """
    Fixture that automatically resets the app's activities to fresh data before each test.
    This is automatically used (autouse=True) for every test to ensure isolation.
    """
    # Clear existing activities
    activities.clear()
    # Populate with fresh test data
    activities.update(activities_with_participants)
    yield
    # Cleanup after test (optional, but good practice)
    activities.clear()
