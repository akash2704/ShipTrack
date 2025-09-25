#!/bin/bash

# Initialize Git repository and push to GitHub

echo "🔧 Initializing Git repository..."

# Initialize git
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: ShipTrack Logistics SaaS with CI/CD pipeline"

# Add remote (replace with your GitHub repo URL)
echo "📝 Add your GitHub repository URL:"
echo "git remote add origin https://github.com/yourusername/shiptrack-logistics-saas.git"
echo ""
echo "Then push with:"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "✅ Git initialized! Add your remote and push to trigger CI/CD."
