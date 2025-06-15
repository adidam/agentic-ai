#!/bin/bash

# Set variables
AWS_ACCOUNT_ID="<AWS_ACCOUNT_ID>"
REGION="<REGION>"
ECR_REPOSITORY="mcp-server"
TASK_DEFINITION="task-definition.json"
CLUSTER_NAME="mcp-cluster"
SERVICE_NAME="mcp-service"

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build and tag the Docker image
docker build -t $ECR_REPOSITORY .
docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPOSITORY:latest

# Push the image to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPOSITORY:latest

# Register the task definition
aws ecs register-task-definition --cli-input-json file://$TASK_DEFINITION

# Update the service
aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --task-definition $ECR_REPOSITORY --force-new-deployment 