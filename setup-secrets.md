# GitHub Secrets Setup

Add these secrets to your GitHub repository:

## Required Secrets

Go to: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### AWS Credentials
```
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
```

### Database
```
DATABASE_URL=postgresql://user:pass@host:5432/shiptrack_db
```

### Security
```
SECRET_KEY=your-super-secret-jwt-key-min-32-chars
CORS_ORIGINS=https://yourdomain.com
```

## AWS Setup

1. Create IAM user with these policies:
   - `AWSLambdaFullAccess`
   - `IAMFullAccess`
   - `AmazonAPIGatewayAdministrator`
   - `CloudFormationFullAccess`

2. Create RDS PostgreSQL database

3. Add secrets to GitHub repository

## Deployment

Push to `main` branch to trigger automatic deployment.
