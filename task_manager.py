"""
task_manager.py
----------------

Handles all task-related logic for the assistant. 
This includes adding, editing, deleting, and retrieving tasks, 
and storing them persistently in a database or file.
"""

import os
import json

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
    

def clear_tasks():
    tasks = {}
    save_tasks(tasks)
    return "All tasks have been cleared."


# Function to handle user commands
def handle_task_command(subcategory, task_info):
    """
    Handles specific task commands based on the subcategory.

    Parameters:
        subcategory (str): The specific task action, e.g., "add task", "list tasks", "delete task".
        task_info (str): Additional information about the task (e.g., description or index).

    Returns:
        str: Result of the command execution.
    """
    if subcategory == "add task":
        return add_task(task_info)
    elif subcategory == "list tasks":
        return list_tasks()
    elif subcategory == "delete task":
        try:
            task_index = str(task_info)
            return delete_task(task_index)
        except ValueError:
            return "Invalid task index. Please provide a valid number."
    else:
        return f"Unknown task command: {subcategory}. Supported commands are 'add task', 'list tasks', and 'delete task'."

# Test the Task Manager
if __name__ == "__main__":
    print(handle_task_command("add task", "Finish the report 1"))
    print(handle_task_command("add task", "Finish the report 2"))
    print(handle_task_command("add task", "Finish the report 3"))
    print(handle_task_command("add task", "Finish the report 4"))
    print(handle_task_command("add task", "Finish the report 5"))
    print(handle_task_command("list tasks", ""))
    
    print(handle_task_command("delete task", "1"))
    print(handle_task_command("delete task", "5"))
    print(handle_task_command("list tasks", ""))
    