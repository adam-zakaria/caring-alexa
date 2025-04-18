from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import json
from datetime import datetime
import pymongo
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)


# Configure OpenAI
openai_api_key = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

# Configure MongoDB
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client["alexa_az"]  # Database name

# Load prompt
current_dir = os.path.dirname(os.path.abspath(__file__))
prompt_path = os.path.join(current_dir, "prompt.txt")

if os.path.exists(prompt_path):
    with open(prompt_path, "r") as f:
        conversation_system_prompt = f.read()
else:
    # Default prompt if file doesn't exist
    conversation_system_prompt = """
    # [System Definition]
    You are a friendly and empathetic chatbot designed to support caregivers.
    Your goal is to help caregivers manage their stress and provide encouragement.
    Be empathetic, thoughtful, and avoid medical diagnoses or advice.
    Listen carefully and respond naturally as if you're talking to the user over the phone.
    """

# Helper function to load schedule
def load_schedule():
    """Load the schedule from the JSON file."""
    schedule_path = os.path.join(current_dir, "schedule.json")
    try:
        if os.path.exists(schedule_path):
            with open(schedule_path, "r") as f:
                return json.load(f)
        else:
            # Fallback schedule if file doesn't exist
            print(f"Warning: Schedule file not found at {schedule_path}")
            return [
                {"activity": "No scheduled activities found", "date_time": "N/A"}
            ]
    except Exception as e:
        print(f"Error loading schedule: {str(e)}")
        return [{"activity": "Error loading schedule", "date_time": "N/A"}]

# OpenAI functions
def gpt_inference(messages, stop=None, model="gpt-4o", **kwargs):
    """Call the OpenAI API with the provided messages."""
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=512,
        stop=stop,
        **kwargs
    )
    return response.choices[0].message.content

@app.route("/alexa_user/<alexa_user_id>/conversation", methods=["POST"])
def conversation(alexa_user_id):
    """
    An endpoint that maintains conversation history in MongoDB.
    """
    # Get user message from request
    user_message = request.get_json()["content"]
    user_id = alexa_user_id

    # Load schedule from JSON file
    schedule = load_schedule()
    schedule_str = '\nschedule:\n' + json.dumps(schedule)
    
    # Get a reference to the mongo conversations collection
    conversations_collection = db['conversations']
    
    # Check if user exists in mongo, create if not
    user = conversations_collection.find_one({"user_id": user_id})
    if not user:
        conversations_collection.insert_one({
            "user_id": user_id,
            "conversation_history": []
        })
        user = conversations_collection.find_one({"user_id": user_id})
    
    # Get conversation history
    """
    schema:
    conversation_history = [
        {
            "role": "user",
            "content": "Hello, how are you?",
            "timestamp": "2023-05-01T12:00:00Z"
        },
        ...]
    """
    conversation_history = user.get("conversation_history", [])
    
    # Add the user message to history
    conversation_history.append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.utcnow().isoformat()
    })

    
    # Get current date and time
    # current_date_time = datetime.utcnow()
    # Set a fixed time for testing (8:00 AM today)
    current_date_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    current_date_time_str = f'\ncurrent_date_time: {current_date_time.strftime("%Y-%m-%d %H:%M:%S")}\n'

    # Get assistant response
    assistant_message = client.responses.create(
        model="gpt-4o",
        instructions=conversation_system_prompt + current_date_time_str + schedule_str,
        input=json.dumps(conversation_history), # dump the conversation history into the input
    ).output_text
    
    # Add assistant response to history
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Update MongoDB with new conversation history
    conversations_collection.update_one(
        {"user_id": user_id},
        {"$set": {"conversation_history": conversation_history}}
    )
    # pretty print the conversation history
    print('--------------------------------')
    print("Conversation History:")
    for msg in conversation_history:
        print(f"{msg['role']}: {msg['content']}")
    print('--------------------------------')
    
    # Return the assistant's response
    return jsonify({
        "role": "assistant",
        "content": assistant_message,
        "user_id": user_id,
        "conversation_length": len(conversation_history)
    })

@app.route("/alexa_user/<alexa_user_id>/last_message", methods=["GET"])
def get_last_message(alexa_user_id):
    """
    Retrieves the last assistant message for a given user.
    If no messages exist, creates a welcome message.
    If the last message was CONVERSATION_END, starts a new conversation.
    """
    print(f"get_last_message called for user: {alexa_user_id}")
    
    # Initialize MongoDB collection for conversations
    conversations_collection = db['conversations']
    
    # Check if user exists, create if not
    user = conversations_collection.find_one({"user_id": alexa_user_id})
    if not user or not user.get("conversation_history"):
        print(f"Path: User doesn't exist or has no conversation history")
        # Create initial greeting message
        greeting_msg = "Hello, thanks for checking in. How are you?"
        
        # Initialize new user with welcome message
        if not user:
            print(f"Sub-path: User doesn't exist at all - creating new user")
            conversations_collection.insert_one({
                "user_id": alexa_user_id,
                "conversation_history": [{
                    "role": "assistant",
                    "content": greeting_msg,
                    "chain_of_thoughts": "",
                    "timestamp": datetime.utcnow().isoformat()
                }]
            })
        else:
            print(f"Sub-path: User exists but has no conversation history")
            # User exists but has no messages
            conversations_collection.update_one(
                {"user_id": alexa_user_id},
                {"$set": {"conversation_history": [{
                    "role": "assistant",
                    "content": greeting_msg,
                    "chain_of_thoughts": "",
                    "timestamp": datetime.utcnow().isoformat()
                }]}}
            )
        
        print(f"Returning greeting message")
        # Return the greeting message
        return jsonify({
            "message": "success", 
            "last_message": {
                "role": "assistant",
                "content": greeting_msg,
                "chain_of_thoughts": ""
            }
        })
    
    # Get conversation history
    conversation_history = user.get("conversation_history", [])
    print(f"User has {len(conversation_history)} messages in history")
    
    # Filter for assistant messages
    assistant_messages = [msg for msg in conversation_history if msg.get("role") == "assistant"]
    print(f"Found {len(assistant_messages)} assistant messages")
    
    if not assistant_messages:
        print(f"Path: User exists but has no assistant messages")
        # Shouldn't happen normally, but handle just in case
        greeting_msg = "Hello, thanks for checking in. How are you?"
        new_message = {
            "role": "assistant",
            "content": greeting_msg,
            "chain_of_thoughts": "",
            "timestamp": datetime.utcnow().isoformat()
        }
        conversation_history.append(new_message)
        conversations_collection.update_one(
            {"user_id": alexa_user_id},
            {"$set": {"conversation_history": conversation_history}}
        )
        print(f"Added greeting message and returning it")
        return jsonify({
            "message": "success", 
            "last_message": {
                "role": "assistant",
                "content": greeting_msg,
                "chain_of_thoughts": ""
            }
        })
    
    # Check if last message was a conversation end
    last_assistant_message = assistant_messages[-1]
    print(f"Last assistant message content starts with: {last_assistant_message.get('content', '')[:50]}...")
    
    if "CONVERSATION_END" in last_assistant_message.get("content", ""):
        print(f"Path: Last message was CONVERSATION_END")
        # Start a new conversation
        greeting_msg = "Hello, thanks for checking in. How are you?"
        new_message = {
            "role": "assistant",
            "content": greeting_msg,
            "chain_of_thoughts": "",
            "timestamp": datetime.utcnow().isoformat()
        }
        # Clear conversation history and add greeting
        conversations_collection.update_one(
            {"user_id": alexa_user_id},
            {"$set": {"conversation_history": [new_message]}}
        )
        print(f"Cleared history, added greeting message, and returning it")
        return jsonify({
            "message": "success", 
            "last_message": {
                "role": "assistant",
                "content": greeting_msg,
                "chain_of_thoughts": ""
            }
        })
    
    # Return the last assistant message
    print(f"Path: Normal return of last assistant message")
    return jsonify({
        "message": "success",
        "last_message": last_assistant_message
    })

@app.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"})

@app.route("/schedule", methods=["GET"])
def get_schedule():
    """Endpoint to retrieve the schedule."""
    # Load schedule from JSON file using the helper function
    schedule = load_schedule()
    return jsonify(schedule)

if __name__ == "__main__":
    # Add better error handling
    try:
        print(f"Starting server on port {os.environ.get('PORT', 5002)}")
        print(f"OpenAI API key configured: {'Yes' if openai.api_key and len(openai.api_key) > 10 else 'No'}")
        print(f"MongoDB URI: {MONGO_URI}")
        
        # Test MongoDB connection
        try:
            mongo_client.server_info()
            print("MongoDB connection successful")
        except Exception as e:
            print(f"MongoDB connection error: {e}")
        
        port = int(os.environ.get("PORT", 5002))
        app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        print(f"Error starting server: {e}") 