#!/bin/bash

# Deployment script for MyCare Assistant Alexa skill

# Set variables
SKILL_NAME="MyCare Assistant"
AWS_PROFILE=${AWS_PROFILE:-default}
LAMBDA_FUNCTION_NAME="mycare-skill-lambda"
LAMBDA_ROLE_NAME="alexa-skill-lambda-role"
REGION=${AWS_REGION:-us-east-1}

echo "Starting deployment of $SKILL_NAME"
echo "Using AWS profile: $AWS_PROFILE"
echo "Region: $REGION"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null
then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if ASK CLI is installed
if ! command -v ask &> /dev/null
then
    echo "ASK CLI is not installed. Please install it first: npm install -g ask-cli"
    exit 1
fi

# Create a deployment package for Lambda
echo "Creating Lambda deployment package..."
mkdir -p package
cp lambda_function.py package/
pip install requests -t package/
cd package
zip -r ../lambda_package.zip .
cd ..
rm -rf package

# Create IAM role for Lambda (if it doesn't exist)
echo "Setting up IAM role..."
ROLE_ARN=$(aws iam get-role --role-name $LAMBDA_ROLE_NAME --query 'Role.Arn' --output text 2>/dev/null || echo "")

if [ -z "$ROLE_ARN" ]; then
    echo "Creating new IAM role: $LAMBDA_ROLE_NAME"
    
    # Create a trust policy document
    cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    # Create the role
    ROLE_ARN=$(aws iam create-role \
        --role-name $LAMBDA_ROLE_NAME \
        --assume-role-policy-document file://trust-policy.json \
        --query 'Role.Arn' --output text)
    
    # Attach basic Lambda execution policy
    aws iam attach-role-policy \
        --role-name $LAMBDA_ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    
    # Wait for role to propagate
    echo "Waiting for IAM role to propagate..."
    sleep 10
    
    rm trust-policy.json
else
    echo "Using existing IAM role: $ROLE_ARN"
fi

# Check if Lambda function exists
LAMBDA_EXISTS=$(aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME 2>/dev/null || echo "")

if [ -z "$LAMBDA_EXISTS" ]; then
    # Create Lambda function
    echo "Creating new Lambda function: $LAMBDA_FUNCTION_NAME"
    aws lambda create-function \
        --function-name $LAMBDA_FUNCTION_NAME \
        --runtime python3.9 \
        --role $ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://lambda_package.zip \
        --timeout 10 \
        --environment "Variables={API_ENDPOINT=http://your-api-endpoint/mongo_conversation}"
else
    # Update Lambda function
    echo "Updating existing Lambda function: $LAMBDA_FUNCTION_NAME"
    aws lambda update-function-code \
        --function-name $LAMBDA_FUNCTION_NAME \
        --zip-file fileb://lambda_package.zip
fi

# Get the Lambda function ARN
LAMBDA_ARN=$(aws lambda get-function \
    --function-name $LAMBDA_FUNCTION_NAME \
    --query 'Configuration.FunctionArn' \
    --output text)

echo "Lambda ARN: $LAMBDA_ARN"

# Update the skill.json file with the Lambda ARN
echo "Updating skill manifest with Lambda ARN..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # MacOS version
    sed -i '' "s|\"uri\": \"https://your-public-endpoint-url/api/alexa/mycare\"|\"uri\": \"$LAMBDA_ARN\"|g" skill.json
else
    # Linux version
    sed -i "s|\"uri\": \"https://your-public-endpoint-url/api/alexa/mycare\"|\"uri\": \"$LAMBDA_ARN\"|g" skill.json
fi

# Create .ask/ask-states.json if it doesn't exist
mkdir -p .ask
if [ ! -f .ask/ask-states.json ]; then
    echo "Creating ASK states file..."
    cat > .ask/ask-states.json << EOF
{
  "profiles": {
    "default": {
      "skillId": "",
      "skillMetadata": {
        "lastDeployHash": ""
      }
    }
  }
}
EOF
fi

# Deploy the skill using ASK CLI
echo "Deploying skill to Alexa Skills Kit..."
ask deploy

echo "Deployment completed! Your skill is now deployed to AWS Lambda and Alexa Skills Kit."
echo "You may need to enable testing in the Alexa Developer Console."
echo "Remember to update the Lambda environment variable 'API_ENDPOINT' with your actual API endpoint." 