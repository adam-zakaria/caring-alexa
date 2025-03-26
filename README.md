# Current
Does flask need to run here...Likely just the button press, which invokes the skill, which talks to the ec2 server (for mongo access). But for button, a device must be available.

# Setup
Ensure mongo is running
populate .env 

## Install MongoDB (Ubuntu)
### Import MongoDB public key
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor

### Add MongoDB repository
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

### Update package list
sudo apt update

### Install MongoDB
sudo apt install -y mongodb-org

# Run

## MongoDB
sudo systemctl start mongod

## Enable MongoDB to start on boot
sudo systemctl enable mongod

FLASK_APP=app.py flask run --host=0.0.0.0 --port=5002

## Converse with Chatty Alexa (preprompted GPT4o)

# Test
## Directly converse with recover LLM (preprompted GPT4o, not through lambda or Alexa)
python tests/mongo_conversation.py # flask server must be running

# Setting up alexa skill
See docs/setup_skill.md
Could not get cli process working, must use console

# Interact with Alexa skill from cli (Optional)
## Clone the skill to localhost
ask init --hosted-skill-id <skill_id>
cd <skill_folder>
ask dialog

# More notes
* The skill takes a few minutes to build when pushed from cli.
* ask deploy should enable a skill (i.e. don't need to enable skill for testing in dashboard)
