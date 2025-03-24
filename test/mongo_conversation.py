import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5002"  # The Flask server runs on port 5002
USER_ID = "test_user_mongo_123"  # Hardcoded user ID matching the endpoint default

def send_conversation_message(message, user_id=USER_ID):
    """
    Send a message to the mongo_conversation endpoint and get the assistant's response.
    This endpoint maintains conversation history in MongoDB.
    """
    # Endpoint URL
    url = f"{BASE_URL}/mongo_conversation"
    
    # Request headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Request payload
    payload = {
        "message": message,
        "user_id": user_id
    }
    
    # Send POST request
    response = requests.post(url, headers=headers, json=payload)
    
    # Print the result
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("\nResponse:")
        print(f"Assistant: {result['content']}")
        print(f"\nConversation length: {result['conversation_length']}")
        return result
    else:
        print("\nError:")
        print(response.text)
        return None

def simulate_conversation():
    """
    Run an interactive conversation session with the MongoDB-backed assistant.
    The conversation history is maintained between messages.
    """
    print(f"\n=== MongoDB-backed Conversation (User ID: {USER_ID}) ===")
    print("Type 'exit' to end the conversation")
    print("----------------------------------")
    
    while True:
        # Get user input
        user_message = input("\nYou: ")
        
        if user_message.lower() in ['exit', 'quit', 'bye']:
            print("Ending conversation.")
            break
        
        # Send message and get response
        result = send_conversation_message(user_message)
        
        if not result:
            print("Failed to get a response. Ending conversation.")
            break
        
        # Check if conversation should end (based on CONVERSATION_END marker)
        if "CONVERSATION_END" in result['content']:
            print("\nThe assistant has ended the conversation.")
            break

if __name__ == "__main__":
    # Check if a message was provided as a command-line argument
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        send_conversation_message(message)
    else:
        # Start interactive conversation
        simulate_conversation() 