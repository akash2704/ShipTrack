#!/bin/bash

# ShipTrack Logistics SaaS Local Deployment Script

echo "🚀 Deploying ShipTrack Logistics SaaS locally..."

# Check if serverless is installed
if ! command -v serverless &> /dev/null; then
    echo "Installing Serverless Framework..."
    npm install -g serverless
fi

# Install serverless plugins
echo "Installing serverless plugins..."
npm install

# Run tests first
echo "Running tests..."
if command -v uv &> /dev/null; then
    uv run pytest -v
else
    python -m pytest -v
fi

if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Deployment aborted."
    exit 1
fi

# Deploy to AWS
echo "Deploying to AWS Lambda..."
serverless deploy --stage prod

echo "✅ Deployment complete!"
echo "Your API is now available at the endpoint shown above."
