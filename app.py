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

def conversation(messages):
    """Process a conversation with the system prompt."""
    return gpt_inference(
        [{"role": "system", "content": conversation_system_prompt}, *messages],
    )

@app.route("/direct_conversation", methods=["POST"])
def direct_conversation():
    """
    A simplified endpoint that calls the LLM directly without user ID or database interaction.
    Just takes a message and returns the LLM response using the custom prompt.
    """
    data = request.json
    message = data.get("message", "")
    
    # Create a simple conversation structure with just this message
    conversation_logs = [
        {"role": "user", "content": message}
    ]
    
    # Call the OpenAI function directly
    assistant_message = conversation(conversation_logs)
    
    # Process the response
    try:
        chain_of_thoughts, assistant_message = assistant_message.split(
            "==============", 1
        )
        assistant_message = assistant_message.strip()
    except ValueError:
        chain_of_thoughts = """physical: not discussed
stress: not discussed
mood: not discussed
communication: not discussed
"""
    
    # Return just the response without database operations
    return jsonify({
        "role": "assistant",
        "content": assistant_message,
        "chain_of_thoughts": chain_of_thoughts
    })

# Temporarily '/mongo_conversation' endpoint
"""
@current_app.route("/alexa_user/<alexa_user_id>/conversation", methods=["POST"])
@api_key_required
def create_conversation_log(alexa_user_id):
"""
@app.route("/alexa_user/<alexa_user_id>/conversation", methods=["POST"])
#@app.route("/conversation", methods=["POST"])
def mongo_conversation(alexa_user_id):
    """
    An endpoint that maintains conversation history in MongoDB.
    Uses a user ID from the request or a default, creating the user if they don't exist.
    """
    message = request.get_json()["content"]
    user_id = alexa_user_id
    #data = request.json
    #message = data.get("message", "")
    #user_id = data.get("user_id", "test_user_mongo_123")  # Default user ID
    
    # Initialize MongoDB collection for conversations
    conversations_collection = db['conversations']
    
    # Check if user exists, create if not
    user = conversations_collection.find_one({"user_id": user_id})
    if not user:
        # Initialize new user with empty conversation history
        conversations_collection.insert_one({
            "user_id": user_id,
            "conversation_history": []
        })
        # Fetch the newly created user
        user = conversations_collection.find_one({"user_id": user_id})
    
    # Get conversation history
    conversation_history = user.get("conversation_history", [])
    
    # Add the new user message to history
    conversation_history.append({
        "role": "user",
        "content": message,
        "timestamp": datetime.utcnow()
    })
    
    # Format for OpenAI API
    conversation_logs = [
        {"role": log["role"], "content": log["content"]}
        for log in conversation_history
    ]
    
    # Call the OpenAI function with full history
    assistant_message = conversation(conversation_logs)
    
    # Process the response
    try:
        chain_of_thoughts, assistant_message = assistant_message.split(
            "==============", 1
        )
        assistant_message = assistant_message.strip()
    except ValueError:
        chain_of_thoughts = """physical: not discussed
stress: not discussed
mood: not discussed
communication: not discussed
"""
    
    # Add assistant response to history
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message,
        "chain_of_thoughts": chain_of_thoughts,
        "timestamp": datetime.utcnow()
    })
    
    # Update MongoDB with new conversation history
    conversations_collection.update_one(
        {"user_id": user_id},
        {"$set": {"conversation_history": conversation_history}}
    )
    
    # Return the assistant's response
    return jsonify({
        "role": "assistant",
        "content": assistant_message,
        "chain_of_thoughts": chain_of_thoughts,
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
        greeting_msg = "Hello, thanks for checking in. How are you managing your caregiving and taking care of yourself?"
        
        # Initialize new user with welcome message
        if not user:
            print(f"Sub-path: User doesn't exist at all - creating new user")
            conversations_collection.insert_one({
                "user_id": alexa_user_id,
                "conversation_history": [{
                    "role": "assistant",
                    "content": greeting_msg,
                    "chain_of_thoughts": "",
                    "timestamp": datetime.utcnow()
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
                    "timestamp": datetime.utcnow()
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
        greeting_msg = "Hello, thanks for checking in. How are you managing your caregiving and taking care of yourself?"
        new_message = {
            "role": "assistant",
            "content": greeting_msg,
            "chain_of_thoughts": "",
            "timestamp": datetime.utcnow()
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
        greeting_msg = "Hello, thanks for checking in. How are you managing your caregiving and taking care of yourself?"
        new_message = {
            "role": "assistant",
            "content": greeting_msg,
            "chain_of_thoughts": "",
            "timestamp": datetime.utcnow()
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