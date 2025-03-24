# Setup
Ensure mongo is running
populate .env 

# Run
FLASK_APP=app.py flask run --host=0.0.0.0 --port=5002

## Converse with Chatty Alexa (preprompted GPT4o)
python tests/mongo_conversation.py # flask server must be running

# Current work
The flask code is be