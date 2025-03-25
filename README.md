# Current
Does flask need to run here...Likely just the button press, which invokes the skill, which talks to the ec2 server (for mongo access). But for button, a device must be available.

# Setup
Ensure mongo is running
populate .env 

# Run
FLASK_APP=app.py flask run --host=0.0.0.0 --port=5002


# Test
## Directly converse with recover LLM (preprompted GPT4o, not through lambda or Alexa)
python tests/mongo_conversation.py # flask server must be running