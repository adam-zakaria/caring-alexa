# MyCare Assistant - Alexa Skill for Caregivers

A complete solution for building and deploying an Alexa skill that provides conversational support for caregivers, powered by OpenAI's GPT models and a custom conversation API.

## Project Overview

This project consists of:

1. **Conversation API**: A Flask API that interacts with OpenAI to provide context-aware conversational responses
2. **Alexa Skill**: Custom Alexa skill that lets users talk to the assistant via voice
3. **Button Integration**: Optional hardware button that can trigger the Alexa skill

## Directory Structure

- `/app.py` - Core Flask application with conversation endpoints
- `/skills/mycare_skill/` - Alexa skill definition and deployment files
- `/button.py` - Script for triggering the skill via a physical button
- `/test_*.py` - Test scripts for the API endpoints

## Setup Instructions

### 1. Set Up the Conversation API

```bash
# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your-openai-api-key"

# Run the API server
python app.py
```

The API will run on port 5002 by default.

### 2. Deploy the Alexa Skill

See the detailed instructions in `/skills/mycare_skill/README.md`, but the basic steps are:

```bash
cd skills/mycare_skill
chmod +x deploy.sh
./deploy.sh
```

This will deploy the skill to AWS Lambda and register it with the Alexa Skills Kit.

### 3. Configure the Button (Optional)

If you want to use a physical button to trigger the skill:

```bash
# For Raspberry Pi with a button connected to GPIO pin 17
python button.py
```

For testing without hardware, the script includes a mock button.

## Testing

You can test various components:

- **API Testing**: 
  ```bash
  python test_direct_conversation.py "Hello, how are you today?"
  python test_mongo_conversation.py
  ```

- **Skill Testing**: Test in the Alexa Developer Console or on your Echo device 
  by saying "Alexa, open my care assistant"

- **Button Testing**: Run `python button.py` to simulate a button press

## API Endpoints

- `/direct_conversation` - Simple endpoint for one-off conversations
- `/mongo_conversation` - Endpoint that maintains conversation history in MongoDB
- `/health` - Simple health check endpoint

## Customization

- Edit `prompt.txt` to change the system prompt for the assistant
- Modify `skills/mycare_skill/interactionModel.json` to change skill phrases and intents
- Update `button.py` to use different hardware configurations

## Deployment

For production deployment:

1. Deploy the Flask API to a public server (AWS, Heroku, etc.)
2. Update the Lambda environment variable `API_ENDPOINT` to point to your deployed API
3. Ensure your API has proper security (HTTPS, authentication if needed)

## License

[Your license information]

## Credits

This project incorporates custom conversation API technology and uses OpenAI's GPT API for natural language processing.