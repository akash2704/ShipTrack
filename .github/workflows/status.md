# CI/CD Status

Add this badge to your README.md:

```markdown
[![CI/CD Pipeline](https://github.com/yourusername/shiptrack-logistics-saas/actions/workflows/deploy.yml/badge.svg)](https://github.com/yourusername/shiptrack-logistics-saas/actions/workflows/deploy.yml)
```

## Workflow Steps

1. **Test Stage**
   - ✅ Checkout code
   - ✅ Setup Python 3.12
   - ✅ Install dependencies with uv
   - ✅ Run pytest tests

2. **Deploy Stage** (only on main branch)
   - ✅ Setup Node.js
   - ✅ Install Serverless Framework
   - ✅ Configure AWS credentials
   - ✅ Deploy to AWS Lambda

## Triggers

- **Push to main/master**: Full CI/CD (test + deploy)
- **Pull Request**: Tests only
- **Manual**: Can be triggered from GitHub Actions tab
