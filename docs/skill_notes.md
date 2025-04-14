# Skill Dashboard (Alexa Sim)
https://developer.amazon.com/alexa/console/ask/test/amzn1.ask.skill.baf61538-539e-4d87-8783-b83916fc2119/development/en_US/

# Lambda Dashboard
https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions

# Requirements
* Backend server must be running (app.py), otherwise lambda will error and the Alexa (conversation) console will not respond as expected:
`FLASK_APP=app.py flask run --host=0.0.0.0 --port=5002`
Also, Flask needs to be run on a machine with a static IP because lambda will need to talk with it. The static IP is configured in config.py
`apiHost = "http://54.167.31.12:5002"`
Currently, this machine is on Adam's EC2.
* Likely, mongo must be running as well, on EC2.

# Skill Flow
The skill flow is complicated so it's best to refresh with an LLM when need be. In the interest of time it won't be perfectly documented here.

The basic idea:
* schedule_proactive_reminders.py uses alexa_api.execute_command('recover demo bot'...)
* en-US.json catches commands sent to Alexa, 
      "invocationName": "recover demo bot"
  gets hit. this triggers the skill. An intent must also get hit after the skill, and the intents get hit based on 'samples' - and ConversationIntent uses a catch-all / wildcard "{text}" and is what will get hit if nothing else matches.
* ConversationIntent maps to ConversationHandler in lambda_function.py. Though first LaunchRequestHandler gets executed (happens first for any intent? Or maybe just the initial skill invocation). There are also further checks in the handlers to determine if they should handle this request, i.e. can_handle(), then handle(). And yes, this skill flow thing follows a request / server model (though lambda is serverless :) ).

class MorningProactiveReminderHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("MorningProactiveReminderIntent")(handler_input)

    def handle(self, handler_input):
        user_id = get_customer_email(handler_input)
        message = "Good morning! How are you feeling today?"
        resp = conversation(user_id, message)
        # ... handle response ...

class AfternoonProactiveReminderHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AfternoonProactiveReminderIntent")(handler_input)

    def handle(self, handler_input):
        user_id = get_customer_email(handler_input)
        message = "Good afternoon! How are you feeling now?"
        resp = conversation(user_id, message)
        # ... handle response ...