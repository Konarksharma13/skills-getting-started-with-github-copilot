"""
Tests for POST /signup and DELETE /signup endpoints.
Uses AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestPostSignup:
    """Test suite for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_valid_student_succeeds(self, client):
        """
        Test that a valid student signup returns 200 and adds the student to participants.
        """
        # Arrange
        activity = "Chess Club"
        email = "newstudent@test.com"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity}"
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Test that signing up for a non-existent activity returns 404.
        """
        # Arrange
        activity = "NonExistent Club"
        email = "test@test.com"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email_returns_400(self, client):
        """
        Test that signing up the same email twice returns 400 and prevents duplicate.
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_with_url_encoded_activity_name(self, client):
        """
        Test that activity names with spaces work when URL-encoded.
        """
        # Arrange
        activity = "Chess Club"
        activity_encoded = "Chess%20Club"
        email = "urltest@test.com"

        # Act
        response = client.post(f"/activities/{activity_encoded}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        
        # Verify student was added to the correct activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]

    def test_signup_missing_email_parameter(self, client):
        """
        Test that missing email parameter returns 422 (validation error).
        """
        # Arrange
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup")

        # Assert
        assert response.status_code == 422  # FastAPI validation error


class TestDeleteSignup:
    """Test suite for the DELETE /activities/{activity_name}/signup endpoint."""

    def test_delete_enrolled_participant_succeeds(self, client):
        """
        Test that removing an enrolled participant returns 200 and removes them.
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity}"
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity]["participants"]

    def test_delete_nonexistent_activity_returns_404(self, client):
        """
        Test that deleting from a non-existent activity returns 404.
        """
        # Arrange
        activity = "NonExistent Club"
        email = "test@test.com"

        # Act
        response = client.delete(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_delete_non_enrolled_student_returns_400(self, client):
        """
        Test that removing a student not enrolled in an activity returns 400.
        """
        # Arrange
        activity = "Chess Club"
        email = "notinlist@test.com"

        # Act
        response = client.delete(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_delete_decreases_participant_count(self, client):
        """
        Test that participant count decreases after deletion.
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])

        # Act
        response = client.delete(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        
        # Verify count decreased
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity]["participants"])
        assert final_count == initial_count - 1


class TestSignupIntegration:
    """Integration tests for signup/delete workflows."""

    def test_signup_delete_signup_cycle(self, client):
        """
        Test that a student can signup, delete, and signup again for the same activity.
        """
        # Arrange
        activity = "Tennis Club"
        email = "alice@test.com"

        # Act - First signup
        signup1 = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert - First signup succeeded
        assert signup1.status_code == 200
        activities1 = client.get("/activities").json()
        assert email in activities1[activity]["participants"]

        # Act - Delete
        delete_response = client.delete(f"/activities/{activity}/signup", params={"email": email})

        # Assert - Delete succeeded
        assert delete_response.status_code == 200
        activities2 = client.get("/activities").json()
        assert email not in activities2[activity]["participants"]

        # Act - Second signup (should succeed now)
        signup2 = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert - Second signup succeeded
        assert signup2.status_code == 200
        activities3 = client.get("/activities").json()
        assert email in activities3[activity]["participants"]

    def test_multiple_students_same_activity(self, client):
        """
        Test that multiple different students can sign up to the same activity.
        """
        # Arrange
        activity = "Drama Club"
        emails = ["student1@test.com", "student2@test.com", "student3@test.com"]

        # Act
        for email in emails:
            response = client.post(f"/activities/{activity}/signup", params={"email": email})
            assert response.status_code == 200

        # Assert
        activities = client.get("/activities").json()
        participants = activities[activity]["participants"]
        assert len(participants) == 3
        for email in emails:
            assert email in participants

    def test_same_email_different_activities(self, client):
        """
        Test that the same student can sign up to multiple different activities.
        """
        # Arrange
        email = "john@test.com"
        activities_to_join = ["Chess Club", "Drama Club", "Science Club"]

        # Act
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup", params={"email": email})
            assert response.status_code == 200

        # Assert
        all_activities = client.get("/activities").json()
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]

    def test_delete_frees_capacity_for_duplicate_check(self, client):
        """
        Test that after deletion, a student can re-signup (duplicate check is based on current state).
        """
        # Arrange
        activity = "Art Club"
        email = "artist@test.com"

        # Act - Signup
        signup1 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert signup1.status_code == 200

        # Act - Try to signup again (should fail)
        duplicate_attempt = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert duplicate_attempt.status_code == 400

        # Act - Delete
        delete_response = client.delete(f"/activities/{activity}/signup", params={"email": email})
        assert delete_response.status_code == 200

        # Act - Signup again (should succeed now)
        signup2 = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert signup2.status_code == 200
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
