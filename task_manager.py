"""
task_manager.py
----------------

Handles all task-related logic for the assistant. 
This includes adding, editing, deleting, and retrieving tasks, 
and storing them persistently in a database or file.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
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

# File to store tasks
TASKS_FILE = ".\\database\\tasks.json"

# Load tasks from file
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

# Save tasks to file
def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)


# Function to add a task
def add_task(task_description):
    if not task_description:
        return "Task description cannot be empty."
    
    tasks = load_tasks()
    tasks[len(tasks)+1] = {"description": task_description, "completed": False}
    save_tasks(tasks)
    return f"Task added: {task_description}"

# Function to list all tasks
def list_tasks():
    tasks = load_tasks()
    if not tasks:
        return "No tasks available."
    return "\n".join([f"{id}. {task['description']} [{task['completed']}]" for id, task in tasks.items()])

# Function to delete a task
def delete_task(task_index):
    tasks = load_tasks()
    try:
        tasks[task_index]["completed"] = True
        save_tasks(tasks)
        return f"Task removed: {tasks[task_index]['description']}"
    except IndexError:
        return "Invalid task number. Please provide a valid task index."
    

def clear_tasks_json():
    tasks = {}
    save_tasks(tasks)
    return "All tasks have been cleared."


def help_task(task_info):
    """
    Returns a system prompt to provide the user with instructions about a specific task.
    If the task is not in the list, returns a corresponding message.
    """
    
    task_list = list_tasks()
    
    print(task_list)
    
    system_prompt = f"""
        You are an assistant helping a user with a specific task from his list.
        
        This is the user's task list:
        {task_list}
        
        If task is not in the user's list return a message such as:
        "The task "<task name>" is not in your current list.
        You can add this task to your list or check the existing tasks for a similar one."
        
        If the task exists in the list:
        Here are the instructions for this task:
        1. Provide a detailed step-by-step guide to accomplish this task.
        2. Suggest resources or tools the user might need.
        3. If the task involves specific technologies or methods, provide examples or best practices.
    """
    
    response = get_model_response(f"Please give me instructions for the task {task_info}", system_prompt)
    
    return response


# Function to handle user commands
def handle_task_command(subcategory, task_info):
    """
    Handles specific task commands based on the subcategory.

    Parameters:
        subcategory (str): The specific task action, e.g., "add", "help", "delete".
        task_info (str): Additional information about the task (e.g., description or index).

    Returns:
        str: Result of the command execution.
    """
    if subcategory == "add":
        return add_task(task_info)
    elif subcategory == "help":
        return help_task(task_info)
    elif subcategory == "delete":
        try:
            task_index = str(task_info)
            return delete_task(task_index)
        except ValueError:
            return "Invalid task index. Please provide a valid number."
    else:
        return f"Unknown task command: {subcategory}. Supported commands are 'add', 'list', and 'delete'."

# Test the Task Manager
if __name__ == "__main__":
    print(handle_task_command("add", "Finish the report 1"))
    print(handle_task_command("add", "Finish the report 2"))
    print(handle_task_command("add", "Finish the report 3"))
    print(handle_task_command("add", "Finish the report 4"))
    print(handle_task_command("add", "Finish the report 5"))
    print(handle_task_command("list", ""))
    
    print(handle_task_command("delete", "1"))
    print(handle_task_command("delete", "5"))
    print(handle_task_command("list", ""))
    