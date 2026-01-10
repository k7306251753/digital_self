from digital_self import DigitalSelf
import os

bot = DigitalSelf()
user_input = "hi can you recognize neeli krishna with 100 points and comments are 'thank you so much for your support'"
user_id = 1 # Assuming Neeli is ID 1

print(f"Testing input: {user_input}")
response_gen = bot.chat(user_input, user_id=user_id)

full_response = ""
for chunk in response_gen:
    full_response += str(chunk)

print(f"Response: {full_response}")
