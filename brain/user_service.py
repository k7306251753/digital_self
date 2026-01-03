import requests
import os

class UserServiceConnector:
    def __init__(self, base_url="http://localhost:8089/empengagement"):
        self.base_url = base_url

    def get_all_users(self):
        """Fetches all participants from the user service."""
        try:
            response = requests.get(f"{self.base_url}/participants")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[UserService] Error fetching users: {e}")
            return []

    def log_message(self, user_id, user_name, role, content):
        """Logs a message to the user service."""
        try:
            payload = {
                "userId": user_id,
                "userName": user_name,
                "role": role,
                "content": content
            }
            requests.post(f"{self.base_url}/comm-log", json=payload)
        except Exception as e:
            print(f"[UserService] Error logging message: {e}")

    def recognize(self, sender_id, receiver_username, comment):
        """Triggers a recognition event."""
        try:
            payload = {
                "senderId": sender_id,
                "receiverUsername": receiver_username,
                "comment": comment
            }
            response = requests.post(f"{self.base_url}/recognize", json=payload)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"Error: {e}"

    def get_recognition_history(self, user_id):
        """Fetches recognition history for a user."""
        try:
            response = requests.get(f"{self.base_url}/recognize/received/{user_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[UserService] Error fetching history: {e}")
            return []

    def get_user_by_id(self, user_id):
        """Fetches a specific participant by ID."""
        try:
            response = requests.get(f"{self.base_url}/participants/{user_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[UserService] Error fetching user {user_id}: {e}")
            return None

    def create_user(self, user_data):
        """Creates a new participant."""
        try:
            response = requests.post(f"{self.base_url}/createpax", json=user_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[UserService] Error creating user: {e}")
            return None

    def update_user(self, user_id, user_data):
        """Updates an existing participant."""
        try:
            response = requests.put(f"{self.base_url}/participants/{user_id}", json=user_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[UserService] Error updating user {user_id}: {e}")
            return None

    def delete_user(self, user_id):
        """Deletes a participant."""
        try:
            response = requests.delete(f"{self.base_url}/participants/{user_id}")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"[UserService] Error deleting user {user_id}: {e}")
            return False
