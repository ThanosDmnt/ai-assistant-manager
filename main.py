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


def classify_input(user_input):
    """
    Classify user input into a category and subcategory.
    """
    delimiter = "```"
    system_message = """
    You are an intelligent assistant designed to understand and process user requests. Your tasks are to:
    1. Classify the user's input into categories and subcategories.
    2. Extract actionable details for each request to allow proper handling.
    Follow these steps to answer the customer queries.
    The customer query will be delimited with three backticks, i.e. ```.

    Guidelines:
    - Supported categories are:
    - "task" with subcategories: "add task", "delete task", "list tasks".
    - "schedule" with subcategories: "add event", "delete event", "view events".
    - "knowledgebase" with subcategories: "search information".
    - "reminder" with subcategories: "add reminder", "delete reminder", "list reminders".
    - Return your response in **JSON format** with two keys:
    - `classification`: A list of objects with `category` and `subcategory` fields.
    - `extracted_information`: A list of extracted actionable details (e.g., tasks, event details, or queries).

    Requirements:
    1. Always ensure the number of `classification` objects matches the number of extracted details.
    2. Be concise and specific in extracting information.
    3. Use appropriate sentence case and remove unnecessary words in the extracted information.

    Examples:
    
    Input: "```Please add a task to finish my project named 'Platon'.```"
    Output:
    {
    "classification": [{"category": "task", "subcategory": "add task"}],
    "extracted_information": ["Finish the Platon project"]
    }

    Input: "```Add a task to finish my project named 'Platon' and to tidy my room.```"
    Output:
    {
    "classification": [
        {"category": "task", "subcategory": "add task"},
        {"category": "task", "subcategory": "add task"}
    ],
    "extracted_information": ["Finish the Platon project", "Tidy my room"]
    }

    Input: "```Please delete task 2 and task 5.```"
    Output:
    {
    "classification": [
        {"category": "task", "subcategory": "delete task"},
        {"category": "task", "subcategory": "delete task"}
    ],
    "extracted_information": ["2", "5"]
    }

    Input: "```Schedule a meeting tomorrow at 3 PM with John.```"
    Output:
    {
    "classification": [{"category": "schedule", "subcategory": "add event"}],
    "extracted_information": ["Meeting with John tomorrow at 3 PM"]
    }

    Input: "```What are my tasks for today?```"
    Output:
    {
    "classification": [{"category": "task", "subcategory": "list tasks"}],
    "extracted_information": ["Tasks for today"]
    }

    Ensure responses strictly follow this JSON format.
    """
    
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimiter}{user_input}{delimiter}"}
    ]
    
    classification_response = get_completion_from_messages(messages)
    return classification_response


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
    classification_response = classify_input(user_input)
    if debug: print("Step 2: Classification and extraction response:", classification_response)

    # Parse classification and extraction response
    try:
        classification_data = eval(classification_response)  # Use `json.loads` for production code
        classifications = classification_data.get("classification", [])
        extracted_information = classification_data.get("extracted_information", [])
        if len(classifications) != len(extracted_information): return "Classifications and extracted information don't match."
    except Exception as e:
        if debug: print("Step 2: Error parsing response:", e)
        return "I'm sorry, I couldn't understand your request."

    if debug: 
        print("Step 2a: Parsed classifications:", classifications)
        print("Step 2b: Parsed extracted information:", extracted_information)

    # Step 3: Handle the requests
    responses = []
    for classification, info in zip(classifications, extracted_information):
        category = classification.get("category")
        subcategory = classification.get("subcategory")

        if category == "task":
            try:
                # Use task_manager to handle the specific task command
                task_response = handle_task_command(subcategory, info)
                responses.append(task_response)
            except Exception as e:
                if debug: print(f"Error handling task command for {subcategory} with info {info}:", e)
                responses.append(f"Error handling task: {info}")
                
        elif category == "schedule":
            if subcategory == "add event":
                responses.append(f"Event added: {info}")
            elif subcategory == "delete event":
                responses.append(f"Event deleted: {info}")
            elif subcategory == "view events":
                responses.append("Displaying all events.")
        elif category == "knowledgebase":
            if subcategory == "search information":
                responses.append(f"Searching for: {info}")
        elif category == "reminder":
            if subcategory == "add reminder":
                responses.append(f"Reminder added: {info}")
            elif subcategory == "delete reminder":
                responses.append(f"Reminder deleted: {info}")
            elif subcategory == "list reminders":
                responses.append("Listing all reminders.")

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
    
    response = process_user_message(user_input, debug=False)
    print(response)
    
    user_input_2 = "Please show me the list of tasks, delete task 1 and show me the tasks again"
    response = process_user_message(user_input_2, debug=False)
    print(response)
    
    
    clear_tasks()
