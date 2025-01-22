from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
from dotenv import load_dotenv
from task_manager import handle_task_command, clear_tasks_json
from scheduler import handle_schedule_action
import utils
import json

# Load environment variables
load_dotenv()

# Set OpenAI API key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize Flask app
app = Flask(__name__)

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
            
            if debug: print(f"Schedule json: {schedule_json}")
            # Call handle_schedule_action with the parsed JSON
            try:
                schedule_action_result = handle_schedule_action(schedule_json)
                responses.append(schedule_action_result)
            except Exception as e:
                if debug: print(f"Error handling schedule action: {e}")
                responses.append("An error occurred while processing your schedule request.")        
        else:
            return f"I couldn't classify your request. Please try again. (category = {category})"
            

    return "\n".join(responses)

@app.route("/")
def home():
    return render_template("base.html")

@app.route("/process", methods=["POST"])
def process_input():
    user_input = json.loads(request.data.decode('utf-8')).get("user_input")  # Get input from the form
    
    response = process_user_message(user_input, debug=False)  # Process the input
    
    return jsonify({"response": response})  # Return the response as JSON

@app.route("/tasks", methods=["GET"])
def get_tasks():
    try:
        with open("database/tasks.json", "r") as f:
            tasks = json.load(f)
        return jsonify(tasks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/clear-tasks", methods=["POST"])
def clear_tasks():
    try:
        clear_tasks_json()
        return jsonify({"message": "Tasks cleared successfully!"}), 200
    except Exception as e:
        print(f"Error clearing tasks: {e}")
        return jsonify({"message": "Failed to clear tasks."}), 500

if __name__ == "__main__":
    app.run(debug=True)
    