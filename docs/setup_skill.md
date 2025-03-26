# Intro
This is general overview or setting up a skill for the ai-caring workflow, which uses lambda. Amazon frequently changes things so these instructions may be out of date, apologies in advance :)

# Initial Setup
* Setup a skill in the Alexa developer console:
https://developer.amazon.com/alexa/console/ask
* Click 'Create Skill'
* Complete the 'choose's with the responses below:
  1. Choose a type of experience
  -> 'Other'
  2. Choose a model
  -> Custom
  3. Hosting services
  -> Alexa-hosted (Python)
  -> US East (N. Virginia)

Click Next

  Templates
  -> Start From Scratch
  Review
  -> Create Skill

The skill should now be viewable in the dev console

# Configuration
This assumes a lambda has been setup. The lambda must be configured to allow the skill to trigger it. ai-caring is doing this manually currently, but it could be nice to do it through the aws lambda cli.

Add Alexa Skills Kit Trigger to your Lambda:
Go to AWS Console
Open your Lambda function (mycare-skill-lambda)
Click on "Configuration" tab
Click on "Triggers" in the left menu
Click "Add trigger"
Select "Alexa" then "Alexa Skills Kit"
Enter your Skill ID (from Alexa Developer Console main page)
Save

Now go back to the skill you've created. Click on the skill and click on the Build tab (top nav) then the Endpoint tab (left nav). Enter the AWS Lambda ARN (which is listed on the main page of the specific Lambda you want to link)

# Enable for Testing
Alexa developer console -> <Your Skill> -> Test (top nav) -> Enable skill testing for Development (dropdown)

Again, could not get this to work from cli

# Set up intents
Long (look at claude chat history) (Recover Alexa Skill overview)(neu/chatty-alexa.code-workspace)

# Simulate alexa





