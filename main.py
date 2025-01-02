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
from task_manager import handle_task_command, clear_tasks
import utils
import json

# Load environment variables
load_dotenv()

# Set OpenAI API key
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)


def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0, max_tokens=500):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens, 
    )
    return response.choices[0].message.content


def get_model_response(user_input, system_message):
    """
    Generates a response from the model based on the provided user query and system prompt.
    """
    delimeter = "```"
    
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimeter}{user_input}{delimeter}"}
    ]
    
    response = get_completion_from_messages(messages)
    return response


def process_user_message(user_input, debug=True):
    """
    Process user input and return appropriate responses based on the classification.
    """
    # Step 1: Check input to see if it flags the Moderation API
    response = client.moderations.create(input=user_input)
    moderation_output = response.results[0]

    if moderation_output.flagged:
        if debug: print("Step 1: Input flagged by Moderation API.")
        return "Sorry, we cannot process this request."

    if debug: print("Step 1: Input passed moderation check.")
    
    # Step 2: Classify the user input
    classification_prompt = utils.get_classification_prompt()
    classification_response = get_model_response(user_input, classification_prompt)
    if debug: print("Step 2: Classification response:", classification_response)

    # Parse classification and extraction response
    try:
        classifications = json.loads(classification_response).get("classification", {})
        details = json.loads(classification_response).get("details", {})
    except Exception as e:
        if debug: print(f"Error parsing classification response: {e}")
        return "I'm sorry, I couldn't understand your request."
    
    if debug: 
        print("Step 2a: Parsed classifications:", classifications)
        print("Step 2b: Parsed extracted information:", details)

    # Step 3: Handle the requests
    responses = []
    for classification, info in zip(classifications, details):
        category = classification.get("category")
        
        if not category:
            return "I couldn't classify your request. Please try again."

        if category == "task":
            tasks_prompt = utils.get_task_prompt()
            task_manager_response = get_model_response(info, tasks_prompt)
            
            # Parse task_manager_response
            try:
                task_action = json.loads(task_manager_response).get("task_action", {})
                task_details = json.loads(task_manager_response).get("details", {})
            except Exception as e:
                if debug: print(f"Error parsing tasks response: {e}")
                return "I'm sorry, I couldn't understand your request."
            
            try:
                # Use task_manager to handle the specific task command
                task_response = handle_task_command(task_action, task_details)
                responses.append(task_response)
            except Exception as e:
                if debug: print(f"Error handling task command for {task_action} with info {task_details}:", e)
                responses.append(f"Error handling task: {task_details}")
                
        elif category == "schedule":
            schedule_prompt = utils.get_schedule_prompt()
            schedule_manager_response = get_model_response(info, schedule_prompt)
            
            # Parse schedule_manager_response
            try:
                schedule_json = json.loads(schedule_manager_response)
            except Exception as e:
                if debug: print(f"Error parsing schedule response: {e}")
                return "I'm sorry, I couldn't understand your request."
            
            responses.append(f"Schedule json: {schedule_json}")
        
        elif category == "reminder":
            reminder_prompt = utils.get_reminder_prompt()
            reminder_manager_response = get_model_response(info, reminder_prompt)
            
            # Parse reminder_manager_response
            try:
                reminder_action = json.loads(reminder_manager_response).get("reminder_action", {})
                reminder_details = json.loads(reminder_manager_response).get("details", {})
            except Exception as e:
                if debug: print(f"Error parsing reminder response: {e}")
                return "I'm sorry, I couldn't understand your request."
            
            responses.append(f"Reminder action: {reminder_action}")
            responses.append(f"Reminder details: {reminder_details}")
        
        elif category == "informations":
            # information_prompt = utils.get_reminder_prompt()
            # information_manager_response = get_model_response(info, reminder_prompt)
            
            responses.append(f"Information: {info}")
            

    return "\n".join(responses)


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
    user_input = "Please add a task to finish the report and also create a reminder for tomorrow to book the cinema tickets"
    bad_user_input = "Please make a reminder to kill someone in two days"
    
    response = process_user_message(user_input, debug=True)
    print(response)
    
    user_input_2 = "Please show me the list of tasks, delete task 1 and show me the tasks again"
    response = process_user_message(user_input_2, debug=True)
    print(response)
    
    
    clear_tasks()
