import json
import requests
import os
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuration
API_ENDPOINT = os.environ.get('API_ENDPOINT', 'http://localhost:5002/mongo_conversation')

def lambda_handler(event, context):
    """
    Main handler for Alexa skill requests.
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Get request type
    request_type = event['request']['type']
    
    # Initialize response
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": ""
            },
            "shouldEndSession": False
        }
    }
    
    # Handle different request types
    if request_type == "LaunchRequest":
        return handle_launch(response)
    elif request_type == "IntentRequest":
        return handle_intent(event, response)
    elif request_type == "SessionEndedRequest":
        return handle_session_ended(response)
    else:
        response["response"]["outputSpeech"]["text"] = "I'm not sure how to handle that request."
        return response

def handle_launch(response):
    """Handle when the skill is launched without a specific intent."""
    response["response"]["outputSpeech"]["text"] = "Welcome to MyCare Assistant. How are you feeling today?"
    return response

def handle_intent(event, response):
    """Handle specific intents from the user."""
    intent_name = event['request']['intent']['name']
    
    # Handle built-in Amazon intents
    if intent_name == "AMAZON.HelpIntent":
        response["response"]["outputSpeech"]["text"] = "You can tell me how you're feeling or ask for caregiving tips. How can I help you today?"
    elif intent_name in ["AMAZON.StopIntent", "AMAZON.CancelIntent"]:
        response["response"]["outputSpeech"]["text"] = "Thank you for using MyCare Assistant. Goodbye!"
        response["response"]["shouldEndSession"] = True
    # Handle our custom conversation intent
    elif intent_name == "ConversationIntent":
        return handle_conversation(event, response)
    # Handle fallback for unrecognized intents
    else:
        response["response"]["outputSpeech"]["text"] = "I'm not sure how to help with that. You can tell me how you're feeling or ask for caregiving tips."
    
    return response

def handle_session_ended(response):
    """Handle when the session ends."""
    # No speech response is needed for SessionEndedRequest
    return response

def handle_conversation(event, response):
    """Process the user's conversation and send it to our API."""
    try:
        # Extract user's message from slots
        slots = event['request']['intent']['slots']
        if 'Message' in slots and 'value' in slots['Message']:
            message = slots['Message']['value']
        else:
            response["response"]["outputSpeech"]["text"] = "I didn't catch what you said. Could you please repeat that?"
            return response
        
        # Get user ID from Alexa request
        user_id = event['session']['user']['userId']
        
        # Call our conversation API
        api_response = call_conversation_api(message, user_id)
        
        if api_response:
            # Get assistant's response
            assistant_message = api_response.get('content', '')
            
            # Check for conversation end marker and remove it
            if "CONVERSATION_END" in assistant_message:
                assistant_message = assistant_message.replace("CONVERSATION_END", "").strip()
                response["response"]["shouldEndSession"] = True
            
            # Set response text
            response["response"]["outputSpeech"]["text"] = assistant_message
        else:
            response["response"]["outputSpeech"]["text"] = "I'm having trouble connecting right now. Please try again later."
    
    except Exception as e:
        logger.error(f"Error handling conversation: {str(e)}")
        response["response"]["outputSpeech"]["text"] = "I'm sorry, something went wrong. Please try again."
    
    return response

def call_conversation_api(message, user_id):
    """Call our backend conversation API."""
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            'message': message,
            'user_id': user_id
        }
        
        response = requests.post(API_ENDPOINT, headers=headers, json=data, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API returned status code {response.status_code}: {response.text}")
            return None
    
    except Exception as e:
        logger.error(f"Error calling conversation API: {str(e)}")
        return None 