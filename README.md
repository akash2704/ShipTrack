# ShipTrack Logistics SaaS

A complete serverless logistics management platform with CI/CD pipeline.

## Features

- 🔐 JWT Authentication & Authorization.
- 📦 Inventory Management
- 🚚 Shipment Tracking
- 📍 Real-time Location Updates
- 💰 Expense Management
- 📊 Financial Dashboard & KPIs
- 💳 Budget Management
- 🔄 WebSocket Real-time Communication
- 🚀 **CI/CD Pipeline with GitHub Actions**

## CI/CD Pipeline

### Automatic Deployment
1. **Tests run** on every push/PR
2. **Deploy to AWS Lambda** on push to `main` branch
3. **Zero-downtime** serverless deployment

### Setup CI/CD

1. **Initialize Git repository:**
   ```bash
   ./init-git.sh
   ```

2. **Create GitHub repository** and add remote:
   ```bash
   git remote add origin https://github.com/yourusername/shiptrack-logistics-saas.git
   git branch -M main
   git push -u origin main
   ```

3. **Add GitHub Secrets** (see `setup-secrets.md`):
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `CORS_ORIGINS`

4. **Push to trigger deployment:**
   ```bash
   git add .
   git commit -m "Deploy to production"
   git push
   ```

## Local Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest -v

# Run locally
uv run uvicorn main:app --reload

# Deploy manually
./deploy.sh
```

## Environment Variables

```env
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://yourdomain.com
```

## Architecture

- **Backend**: FastAPI with async SQLAlchemy
- **Database**: PostgreSQL (AWS RDS)
- **Authentication**: JWT tokens
- **Deployment**: AWS Lambda + API Gateway
- **CI/CD**: GitHub Actions
- **Testing**: Pytest with async support
