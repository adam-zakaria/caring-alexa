# MyCare Assistant Alexa Skill

This directory contains the necessary files to deploy the MyCare Assistant skill to Alexa.

## Prerequisites

- [AWS CLI](https://aws.amazon.com/cli/) installed and configured
- [ASK CLI](https://developer.amazon.com/en-US/docs/alexa/smapi/quick-start-alexa-skills-kit-command-line-interface.html) installed and configured
- An AWS account with permissions to create Lambda functions and IAM roles
- An Amazon Developer account

## Files in this Directory

- `skill.json` - Skill manifest that defines the skill's metadata
- `interactionModel.json` - Defines the voice interaction model for the skill
- `lambda_function.py` - The Lambda function code that handles skill requests
- `deploy.sh` - Deployment script to automate the deployment process

## Setup and Deployment

1. Make sure your API endpoint is ready and accessible
   - The default endpoint is set to `http://localhost:5002/mongo_conversation`
   - For production, update this to your publicly accessible API endpoint

2. Make the deployment script executable:
   ```
   chmod +x deploy.sh
   ```

3. Run the deployment script:
   ```
   ./deploy.sh
   ```

   This script will:
   - Create a Lambda deployment package
   - Create or update the IAM role for Lambda execution
   - Create or update the Lambda function
   - Deploy the skill to the Alexa Skills Kit

4. After deployment, you'll need to enable testing in the Alexa Developer Console:
   - Go to the [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
   - Select your skill
   - Go to the "Test" tab
   - Change the dropdown from "Off" to "Development"

## Testing the Skill

You can test the skill in the following ways:

1. **Alexa Developer Console**: Use the test tab to simulate interactions
2. **Alexa-enabled Device**: If your Amazon account is the same as your developer account, say "Alexa, open my care assistant"
3. **Button Trigger**: Use the provided button.py script to trigger the skill programmatically

## Customization

- Update the `interactionModel.json` to add more sample utterances or intents
- Modify `lambda_function.py` to add new features or change the conversation flow
- Update the `API_ENDPOINT` in the Lambda environment variables to point to your backend

## Troubleshooting

If you encounter issues:

1. Check CloudWatch logs for Lambda execution errors
2. Verify that your API endpoint is accessible from AWS Lambda
3. Ensure your skill is enabled for testing
4. Check that the interaction model is correctly defined

## Further Resources

- [Alexa Skills Kit Documentation](https://developer.amazon.com/en-US/docs/alexa/ask-overviews/build-skills-with-the-alexa-skills-kit.html)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html) 