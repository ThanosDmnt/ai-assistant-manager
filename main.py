"""
main.py
--------

This is the entry point for the AI-Powered Personal Assistant. 
It initializes the assistant, orchestrates interactions with the user, 
and integrates all the core functionalities: task management, scheduling, 
knowledge base search, and reminders.
"""

from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)


# Test the API connection
def test_chatgpt():
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Πες: Γεια!"}],
            max_tokens=50
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print("Error connecting to OpenAI API:", e)


if __name__ == "__main__":
    test_chatgpt()
