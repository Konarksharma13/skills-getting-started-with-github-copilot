"""
Tests for GET /activities endpoint.
Uses AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivities:
    """Test suite for the GET /activities endpoint."""

    def test_get_all_activities_returns_200(self, client):
        """
        Test that GET /activities returns HTTP 200 and all activities.
        """
        # Arrange
        expected_activity_count = 9

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_response_structure(self, client):
        """
        Test that each activity in the response has the correct structure.
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        for activity_name, activity_details in activities.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_details, dict)
            assert required_fields == set(activity_details.keys())
            assert isinstance(activity_details["description"], str)
            assert isinstance(activity_details["schedule"], str)
            assert isinstance(activity_details["max_participants"], int)
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_participant_counts(self, client):
        """
        Test that participant counts and availability are accurate.
        """
        # Arrange
        # Chess Club should have 2 participants initially

        # Act
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]

        # Assert
        assert response.status_code == 200
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
        # max_participants = 12, participants = 2, so 10 spots left
        assert chess_club["max_participants"] == 12

    def test_get_activities_empty_participant_lists(self, client):
        """
        Test that new activities with no participants show empty participant lists.
        """
        # Arrange
        # Basketball Team should start with no participants

        # Act
        response = client.get("/activities")
        activities = response.json()
        basketball = activities["Basketball Team"]

        # Assert
        assert response.status_code == 200
        assert len(basketball["participants"]) == 0
        assert basketball["participants"] == []
