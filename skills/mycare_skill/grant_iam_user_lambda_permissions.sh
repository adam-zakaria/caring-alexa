# THIS DOES NOT WORK - the previous version deployed, but did not work. This does not even deploy.
# The solution we went with - go into the IAM permissions and manually add: AWSLambda_FullAccess

# Create the policy document
cat > lambda-deploy-policy-full.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:CreateRole",
                "iam:GetRole",
                "iam:PassRole",
                "iam:AttachRolePolicy",
                "iam:DetachRolePolicy",
                "iam:PutRolePolicy",
                "iam:ListRolePolicies",
                "iam:ListAttachedRolePolicies"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Create the policy
aws iam create-policy --policy-name LambdaDeployPolicyFull --policy-document file://lambda-deploy-policy-full.json

# Attach the policy to your user
aws iam attach-user-policy --user-name adam --policy-arn arn:aws:iam::462099094434:policy/LambdaDeployPolicyFull