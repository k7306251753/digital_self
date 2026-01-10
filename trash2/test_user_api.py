import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain.user_service import UserServiceConnector
from digital_self import DigitalSelf

class TestUserServiceIntegration(unittest.TestCase):
    @patch('requests.get')
    def test_get_all_users(self, mock_get):
        # Mocking the Spring Boot response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"userName": "test1", "fullName": "Test User 1"},
            {"userName": "test2", "fullName": "Test User 2"}
        ]
        mock_get.return_value = mock_response

        connector = UserServiceConnector()
        users = connector.get_all_users()
        
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]['userName'], "test1")

    def test_intent_detection(self):
        # We need to mock the user service inside the bot
        bot = DigitalSelf()
        bot.user_service = MagicMock()
        bot.user_service.get_all_users.return_value = [
            {"userName": "k7306251753", "fullName": "Neeli Krishna"}
        ]

        # Test intent detection in chat
        generator = bot.chat("get all users")
        response = "".join(list(generator))
        
        self.assertIn("Neeli Krishna", response)
        self.assertIn("k7306251753", response)

if __name__ == "__main__":
    unittest.main()
