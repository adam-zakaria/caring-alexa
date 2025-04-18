# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
from datetime import datetime
import ask_sdk_core.utils as ask_utils
import config
import requests
from ask_sdk_core.dispatch_components import (
    AbstractExceptionHandler,
    AbstractRequestHandler,
)
from ask_sdk_model.ui.ask_for_permissions_consent_card import (
    AskForPermissionsConsentCard,
)
from ask_sdk_core.exceptions import SerializationException
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk.standard import StandardSkillBuilder
import json
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_schedule():
    """Fetch the schedule from the API endpoint."""
    try:
        resp = requests.get(
            config.apiHost + "/schedule",
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error(f"Failed to fetch schedule: Status code {resp.status_code}")
            return [{"activity": "Error loading schedule", "date_time": "N/A"}]
    except Exception as e:
        logger.error(f"Error fetching schedule: {str(e)}")
        return [{"activity": "Error loading schedule", "date_time": "N/A"}]


def to_speech(handler_input, response):
    break_audio = ' <break time="10s" /> '
    sound_bank_audio = "<prosody volume='silent'> . </prosody>"
    # speak_output = response + break_audio*18 + sound_bank_audio
    speak_output = response
    ask_output = (
        "Anything else I can help? You can repeat your sentence."
        + break_audio * 3
        + sound_bank_audio
    )

    return handler_input.response_builder.speak(speak_output).ask(ask_output).response


def updatePatient(patient_id: int, *args, **kwargs):
    try:
        resp = requests.patch(
            config.apiHost + f"/patients/{patient_id}",
            json=kwargs,
            timeout=10
        )
        logger.info(resp.json())
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"API error in updatePatient: {str(e)}")
        return False


def getLastMessage(alexa_user_id: str):
    try:
        resp = requests.get(
            config.apiHost + f"/alexa_user/{alexa_user_id}/last_message",
            timeout=10
        )
        logger.info("getLastMessage")
        logger.info(resp.json())
        return resp
    except Exception as e:
        logger.error(f"API error in getLastMessage: {str(e)}")
        return None


def recordAlexaID(alexa_user_id: str):
    try:
        resp = requests.post(
            config.apiHost + f"/alexa_user/{alexa_user_id}/create_note",
            timeout=10
        )
        logger.info("recordAlexaID")
        logger.info(resp.json())
        return resp
    except Exception as e:
        logger.error(f"API error in recordAlexaID: {str(e)}")
        return None


def conversationEnded(alexa_user_id: str):
    try:
        resp = requests.post(
            config.apiHost + f"/alexa_user/{alexa_user_id}/session_end",
            json={},
            timeout=10
        )
        logger.info(resp.json())
        return resp.status_code == 200
    except Exception as e:
        print(f"API error in conversationEnded: {str(e)}")
        logger.error(f"API error in conversationEnded: {str(e)}")
        return False


def conversation(alexa_user_id: str, content: str) -> requests.Response:
    # content is the user message
    try:
        resp = requests.post(
            config.apiHost + f"/alexa_user/{alexa_user_id}/conversation",
            json={"content": content},
            timeout=10
        )
        return resp
    except Exception as e:
        logger.error(f"API error in conversation: {str(e)}")
        return None


class EmailPermissionDenied(Exception):
    pass


def get_customer_email(handler_input: HandlerInput) -> str:
    # DEVELOPMENT ONLY: Return a hardcoded email for testing
    return "test@example.com"
    
    # Comment out or remove the original code below during testing
    # ups_client = handler_input.service_client_factory.get_ups_service()
    # result = ups_client.get_profile_email()
    # logger.info(result)
    # if not isinstance(result, str):
    #     raise EmailPermissionDenied
    # return result


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        logger.info("LaunchRequestHandler")
        logger.info(handler_input.request_envelope)
        user_id = get_customer_email(handler_input)

        fresh_greeting = "Hi I'm Robin, your AI Caring assistant! How can I help you today?"  # If we can't get the last message, use this greeting
        
        try:
            last_message = getLastMessage(user_id)
            # Can't get the last message, send fresh greeting
            if last_message is None or last_message.status_code != 200:
                speak_output = fresh_greeting
                return to_speech(handler_input, speak_output)
            
            last_message_json = last_message.json()
            # Got the last message, send last message
            if last_message_json.get("message") == "success":
                speak_output = last_message_json["last_message"]["content"]
                logger.info(f"last_message: {speak_output=}")
                if "CONVERSATION_END" in speak_output:
                    speak_output = "Happy to help you again! What can I do for you?"
            else:
                speak_output = fresh_greeting
        except Exception as e:
            logger.error(f"Error in LaunchRequestHandler: {str(e)}")
            speak_output = fresh_greeting
        
        logger.info(f"{speak_output=}")
        return to_speech(handler_input, speak_output)


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.CancelIntent")(
            handler_input
        ) or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("CancelOrStopIntentHandler")
        logger.info(handler_input.request_envelope)
        user_id = get_customer_email(handler_input)
        if conversationEnded(user_id):
            logger.info("Session ended")
        else:
            logger.error("Failed to end session")
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder.speak(speak_output)
            .set_should_end_session(True)
            .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        logger.info("SessionEndedRequestHandler")
        logger.info(handler_input.request_envelope)
        user_id = get_customer_email(handler_input)
        if conversationEnded(user_id):
            logger.info("Session ended")
        else:
            logger.error("Failed to end session")

        return handler_input.response_builder.response


class MorningProactiveReminderHandler(AbstractRequestHandler):
    """Handler for morning proactive reminders."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        # Only handle the exact "morning check in" intent
        return ask_utils.is_intent_name("MorningProactiveReminderIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("MorningProactiveReminderHandler")
        logger.info(handler_input.request_envelope)
        user_id = get_customer_email(handler_input)

        # Get time, date, weather and location
        location = "Atlanta, GA"
        current_time = datetime.now().strftime("%I:%M %p")
        current_date = datetime.now().strftime("%A, %B %d")
        weather = "Sunny"  # TODO: Replace with actual openweathermap api call
        username = "John"  # TODO: Replace with actual username from database

        # Fetch schedule from API
        schedule = load_schedule()

        # Create JSON data structure for the LLM
        morning_data = {
            "type": "morning_checkin",
            "context": {
                "username": username,
                "time": current_time,
                "date": current_date,
                "weather": weather,
                "location": location
            },
            "schedule": schedule
        }

        # Convert to JSON string
        message = json.dumps(morning_data)
        
        # Send to LLM
        resp = conversation(user_id, message)
        
        if resp is None:
            speak_output = "Sorry, I'm having trouble connecting right now. Please try again later."
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response
            
        if resp.status_code != 200:
            logger.error(resp.text)
            speak_output = "Sorry, I'm having trouble processing your request. Let's try again."
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response
        
        response_json = resp.json()
        speak_output = response_json.get("content", "Sorry, I didn't understand that.")
        
        if "CONVERSATION_END" in speak_output:
            conversationEnded(user_id)
            return (
                handler_input.response_builder.speak(
                    speak_output.replace("CONVERSATION_END", "")
                )
                .set_should_end_session(True)
                .response
            )
        
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response


class AfternoonProactiveReminderHandler(AbstractRequestHandler):
    """Handler for afternoon proactive reminders."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        # Only handle the exact "afternoon check in" intent
        return ask_utils.is_intent_name("AfternoonProactiveReminderIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("AfternoonProactiveReminderHandler")
        logger.info(handler_input.request_envelope)
        user_id = get_customer_email(handler_input)
        
        # Get time and username
        current_time = datetime.now().strftime("%I:%M %p")
        username = "John"  # TODO: Replace with actual username from database
        
        # Fetch schedule from API
        schedule = load_schedule()
        
        # Filter schedule for afternoon - only show events after current time
        try:
            current_time_obj = datetime.strptime(current_time, "%I:%M %p")
            afternoon_schedule = []
            for event in schedule:
                try:
                    event_time = datetime.strptime(event["date_time"], "%I:%M %p")
                    if event_time > current_time_obj:
                        afternoon_schedule.append(event)
                except ValueError:
                    # If time parsing fails, include the event anyway
                    afternoon_schedule.append(event)
        except ValueError:
            # If parsing current time fails, use the full schedule
            afternoon_schedule = schedule
        
        # Notifications - can still be defined here as they may be specific to the afternoon check-in
        notifications = [
            {
                "type": "reminder",
                "message": "Don't forget to drink water throughout the day"
            },
            {
                "type": "schedule_change",
                "message": "Your doctor's appointment for tomorrow has been rescheduled to 10:00 AM"
            }
        ]
        
        # Create JSON data structure for the LLM
        afternoon_data = {
            "type": "afternoon_checkin",
            "context": {
                "username": username,
                "time": current_time
            },
            "schedule": afternoon_schedule,
            "notifications": notifications
        }
        
        # Convert to JSON string
        message = json.dumps(afternoon_data)
        
        resp = conversation(user_id, message)
        
        if resp is None:
            speak_output = "Sorry, I'm having trouble connecting right now. Please try again later."
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response
            
        if resp.status_code != 200:
            logger.error(resp.text)
            speak_output = "Sorry, I'm having trouble processing your request. Let's try again."
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response
        
        response_json = resp.json()
        speak_output = response_json.get("content", "Sorry, I didn't understand that.")
        
        if "CONVERSATION_END" in speak_output:
            conversationEnded(user_id)
            return (
                handler_input.response_builder.speak(
                    speak_output.replace("CONVERSATION_END", "")
                )
                .set_should_end_session(True)
                .response
            )
        
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response


class ConversationHandler(AbstractRequestHandler):
    """Handler for all conversation intents as a catch-all."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        # This handler will catch ALL intent requests and launch requests
        # It's crucial this handler is registered LAST
        intent_name = None
        if ask_utils.is_request_type("IntentRequest")(handler_input):
            intent_name = handler_input.request_envelope.request.intent.name
            logger.info(f"ConversationHandler - Checking if can handle intent: {intent_name}")
        return True

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        if ask_utils.is_request_type("LaunchRequest")(handler_input):
            message = "hello"
        else:
            intent_name = handler_input.request_envelope.request.intent.name
            logger.info(f"ConversationHandler - Handling intent: {intent_name}")
            
            # Try to get the text slot if it exists
            message = ask_utils.get_slot_value(handler_input, "text") or ""
            
            # If no text slot or it's empty, fallback to the intent name
            if not message:
                message = (
                    intent_name
                    .replace("Intent", "")
                    .replace("AMAZON.", "")
                )
        
        logger.info("ConversationHandler - Catch All")
        logger.info(f"message: {message}")
        
        user_id = get_customer_email(handler_input)
        logger.info(user_id)
        
        try:
            resp = conversation(user_id, message)
            
            # Handle case where API call returned None
            if resp is None:
                speak_output = "Sorry, I'm having trouble connecting right now. Please try again later."
                return handler_input.response_builder.speak(speak_output).ask(speak_output).response
                
            logger.info(f"Response status code: {resp.status_code}")
            
            if resp.status_code == 404:
                logger.error(resp.text)
                speak_output = "I don't recognize you yet. Please say 'please note my alexa ID' and contact system administrator."
                return handler_input.response_builder.speak(speak_output).ask(speak_output).response
            elif resp.status_code != 200:
                logger.error(resp.text)
                speak_output = "Sorry, I'm having trouble processing your request. Let's try again."
                return handler_input.response_builder.speak(speak_output).ask(speak_output).response
            
            response_json = resp.json()
            speak_output = response_json.get("content", "Sorry, I didn't understand that.")
            logger.info(f"{speak_output=}")
            
            if "CONVERSATION_END" in speak_output:
                conversationEnded(user_id)
                return (
                    handler_input.response_builder.speak(
                        speak_output.replace("CONVERSATION_END", "")
                    )
                    .set_should_end_session(True)
                    .response
                )
            
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response
            
        except Exception as e:
            logger.error(f"Error in ConversationHandler: {str(e)}")
            speak_output = "Sorry, I'm having trouble with your request. Let's try again."
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors."""

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        if isinstance(exception, EmailPermissionDenied) or (
            isinstance(exception, SerializationException)
            and "ACCESS_DENIED" in str(exception)
        ):
            return (
                handler_input.response_builder.speak(
                    "Please grant permission to access your email address to associate your alexa account with your participant ID"
                )
                .set_card(
                    AskForPermissionsConsentCard(
                        permissions=["alexa::profile:email:read"],
                    )
                )
                .response
            )
        logger.info(handler_input.request_envelope)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

sb = StandardSkillBuilder()

# All specific intents MUST come before the ConversationHandler
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(MorningProactiveReminderHandler())
sb.add_request_handler(AfternoonProactiveReminderHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# ConversationHandler MUST be last as it will catch everything else
sb.add_request_handler(ConversationHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
