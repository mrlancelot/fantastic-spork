# Deployment Guide

This guide provides comprehensive instructions for deploying the TravelAI application to various hosting platforms.

## Prerequisites

Before deploying, ensure you have:

1. **Environment Variables** configured:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   CLERK_SECRET_KEY=your_clerk_secret_key
   VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
   VITE_CONVEX_URL=your_convex_url
   CONVEX_URL=your_convex_url
   CONVEX_DEPLOYMENT=your_convex_deployment
   ```

2. **Dependencies** properly specified:
   - Frontend: Check `frontend/package.json`
   - Backend: Check `backend/requirements.txt`

3. **Production Build** tested locally:
   ```bash
   cd frontend && npm run build
   cd ../backend && fastapi run src/main.py
   ```

## Architecture Overview

The application consists of three main components:

1. **Frontend**: React SPA built with Vite
2. **Backend**: FastAPI Python server
3. **Database**: Convex real-time database

In production, the FastAPI server serves both the API endpoints and the static React build files.

## Deployment Options

### 1. Docker Deployment

Docker provides a consistent environment across different platforms.

#### Building the Docker Image

```bash
# From the root directory
docker build -t travelai .
```

The Dockerfile uses a multi-stage build:
- **Stage 1**: Builds the React frontend using Node.js
- **Stage 2**: Sets up the Python backend and copies the built frontend

#### Running the Container

```bash
# With environment file
docker run -p 8000:8000 --env-file .env travelai

# With individual environment variables
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e CLERK_SECRET_KEY=your_key \
  -e CONVEX_URL=your_url \
  travelai
```

#### Docker Compose (Optional)

Create a `docker-compose.yml`:
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
```

Run with: `docker-compose up -d`

### 2. Vercel Deployment

Vercel offers serverless deployment with automatic scaling.

#### Initial Setup

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy from root directory**:
   ```bash
   vercel
   ```

3. **Follow the prompts**:
   - Select or create a project
   - Choose the root directory
   - Accept the default build settings

#### Configuration Details

The `vercel.json` file configures:
- **Build Process**: Builds frontend and prepares backend
- **Serverless Function**: Backend API runs as a Vercel Function
- **Routing**: Handles API routes and client-side routing
- **Environment**: Sets Python path for imports

#### Environment Variables

Set in Vercel Dashboard:
1. Go to Project Settings → Environment Variables
2. Add all required variables
3. Redeploy for changes to take effect

#### Custom Domain

1. Go to Project Settings → Domains
2. Add your domain
3. Configure DNS as instructed

### 3. Render Deployment

Render provides a simple deployment process with free hosting tier.

#### Setup Process

1. **Create a new Web Service** on [Render Dashboard](https://dashboard.render.com)

2. **Connect your GitHub repository**

3. **Configure the service**:
   - **Name**: Your app name
   - **Environment**: Docker
   - **Branch**: main (or your default)
   - **Docker Command**: (uses Dockerfile CMD)

4. **Add Environment Variables**:
   - Click "Environment" tab
   - Add all required variables

5. **Deploy**: Click "Create Web Service"

#### Render Configuration

Render automatically:
- Detects the Dockerfile
- Builds the Docker image
- Deploys with health checks
- Provides HTTPS endpoint

### 4. AWS Deployment

For AWS deployment, you have several options:

#### AWS App Runner

1. **Build and push to ECR**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [your-ecr-uri]
   docker build -t travelai .
   docker tag travelai:latest [your-ecr-uri]/travelai:latest
   docker push [your-ecr-uri]/travelai:latest
   ```

2. **Create App Runner service**:
   - Use AWS Console or CLI
   - Select ECR as source
   - Configure port 8000
   - Add environment variables

#### AWS ECS with Fargate

1. **Create task definition** with your container
2. **Create ECS service** with ALB
3. **Configure auto-scaling** as needed

### 5. Google Cloud Run

Cloud Run offers serverless container deployment:

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/[PROJECT-ID]/travelai

# Deploy to Cloud Run
gcloud run deploy travelai \
  --image gcr.io/[PROJECT-ID]/travelai \
  --platform managed \
  --port 8000 \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=your_key,CLERK_SECRET_KEY=your_key"
```

### 6. Heroku Deployment

1. **Create `heroku.yml`**:
   ```yaml
   build:
     docker:
       web: Dockerfile
   ```

2. **Deploy**:
   ```bash
   heroku create your-app-name
   heroku stack:set container
   git push heroku main
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set GEMINI_API_KEY=your_key
   ```

## Convex Setup

Convex deployment is separate from the main application:

1. **Deploy Convex functions**:
   ```bash
   cd frontend
   npx convex deploy
   ```

2. **Get deployment URL**:
   - Check Convex dashboard
   - Update CONVEX_URL in your deployment

3. **Configure Clerk webhook** (if using):
   - Add Convex webhook URL in Clerk dashboard
   - Configure user sync events

## Production Considerations

### Environment Variables

1. **Security**:
   - Use platform-specific secret management
   - Never commit `.env` files
   - Rotate keys regularly

2. **Required Variables**:
   ```
   # Backend
   GEMINI_API_KEY        # Google AI API key
   CLERK_SECRET_KEY      # Clerk backend key
   CONVEX_URL           # Convex deployment URL
   CONVEX_DEPLOYMENT    # Convex deployment name
   
   # Frontend (build-time)
   VITE_CLERK_PUBLISHABLE_KEY  # Clerk frontend key
   VITE_CONVEX_URL            # Convex URL for frontend
   ```

### CORS Configuration

Update `backend/src/api.py` for production domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### SSL/HTTPS

Most platforms provide automatic SSL. For custom deployments:
- Use Let's Encrypt with Certbot
- Configure reverse proxy (Nginx/Caddy)
- Update Clerk and Convex URLs to use HTTPS

### Performance Optimization

1. **Enable compression**:
   ```python
   # In backend/src/main.py
   from fastapi.middleware.gzip import GZipMiddleware
   app.add_middleware(GZipMiddleware, minimum_size=1000)
   ```

2. **Set cache headers** for static files

3. **Use CDN** for static assets if needed

### Monitoring

1. **Health Check Endpoint**:
   - `/hello` endpoint for basic health check
   - Add more comprehensive health checks if needed

2. **Logging**:
   - Configure structured logging
   - Use platform-specific log aggregation

3. **Error Tracking**:
   - Integrate Sentry or similar
   - Monitor API errors and performance

## Troubleshooting

### Common Issues

1. **Port Configuration**:
   - Ensure `PORT` environment variable is respected
   - Default port is 8000

2. **Static Files Not Serving**:
   - Check `public/` directory exists
   - Verify build process completed

3. **API Routes Not Working**:
   - Check URL rewriting configuration
   - Verify CORS settings

4. **Memory Issues**:
   - Increase container memory limits
   - Optimize Python imports

### Debug Steps

1. **Test Docker build locally**:
   ```bash
   docker build . -t test
   docker run -p 8000:8000 test
   ```

2. **Check logs**:
   - Platform-specific log viewers
   - Add debug logging temporarily

3. **Verify environment**:
   - Use `/test-env` endpoint
   - Check all variables are set

### Platform-Specific Issues

#### Vercel
- **Function Size**: Keep under 50MB compressed
- **Timeout**: Maximum 10 seconds for hobby plan
- **Cold Starts**: Expect initial request delays

#### Docker
- **Multi-platform builds**: Use buildx for ARM support
- **Layer Caching**: Order Dockerfile for optimal caching

#### Render
- **Disk Storage**: Ephemeral by default
- **Sleep Mode**: Free tier sleeps after inactivity

## Scaling Considerations

### Horizontal Scaling
- Application is stateless (state in Convex)
- Can run multiple instances
- Load balancer handles distribution

### Vertical Scaling
- Increase container resources
- Monitor memory usage
- Profile Python performance

### Caching Strategy
- Implement Redis for AI response caching
- Use browser caching for static assets
- Consider edge caching with CDN

## Backup and Recovery

1. **Convex Data**:
   - Use Convex export features
   - Schedule regular backups

2. **Environment Variables**:
   - Document all variables
   - Store securely offline

3. **Code Repository**:
   - Tag releases
   - Maintain deployment branches

## Continuous Deployment

### GitHub Actions Example

```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

### Deployment Checklist

- [ ] Environment variables configured
- [ ] Convex deployed and connected
- [ ] CORS settings updated
- [ ] SSL/HTTPS enabled
- [ ] Health checks passing
- [ ] Error tracking configured
- [ ] Monitoring setup
- [ ] Backup strategy in place
- [ ] Documentation updated