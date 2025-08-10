# TravelAI Deployment Guide

## 🚀 Deployment Options

### 1. Docker Deployment (Recommended)

#### Build and run with Docker Compose:
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Build backend only:
```bash
cd backend
docker build -t travelai-backend .
docker run -p 8000:8000 --env-file ../.env travelai-backend
```

### 2. Vercel Deployment (Serverless)

#### Prerequisites:
- Vercel CLI installed (`npm i -g vercel`)
- Vercel account

#### Deploy:
```bash
# From project root
vercel

# For production
vercel --prod
```

#### Environment Variables:
Set these in Vercel dashboard:
- `GEMINI_API_KEY`
- `TAVILY_API_KEY`
- `OPENROUTER_API_KEY`
- `CLERK_SECRET_KEY`
- `CONVEX_URL`
- `CONVEX_DEPLOYMENT`

### 3. Traditional Server Deployment

#### On Ubuntu/Debian:
```bash
# Install Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv

# Clone repository
git clone <repo-url>
cd fantastic-spork/backend

# Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps

# Run with systemd (create service file)
sudo nano /etc/systemd/system/travelai.service
```

#### Systemd service file:
```ini
[Unit]
Description=TravelAI Backend API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/fantastic-spork/backend
Environment="PATH=/home/ubuntu/fantastic-spork/backend/venv/bin"
EnvironmentFile=/home/ubuntu/fantastic-spork/.env
ExecStart=/home/ubuntu/fantastic-spork/backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Enable and start service:
```bash
sudo systemctl enable travelai
sudo systemctl start travelai
sudo systemctl status travelai
```

### 4. Railway/Render Deployment

#### Railway:
1. Connect GitHub repo
2. Add environment variables
3. Set start command: `python main.py`
4. Deploy

#### Render:
1. Create new Web Service
2. Connect GitHub repo
3. Build command: `pip install -r requirements.txt && playwright install chromium`
4. Start command: `python main.py`

## 🔧 Production Considerations

### 1. Environment Variables
Create `.env.production`:
```env
# Required
GEMINI_API_KEY=your_production_key
TAVILY_API_KEY=your_production_key
SCRAPER_HEADLESS=true

# Optional but recommended
OPENROUTER_API_KEY=your_production_key
CLERK_SECRET_KEY=your_production_key
CONVEX_URL=your_production_url
CONVEX_DEPLOYMENT=production

# Performance
WORKERS=4
```

### 2. Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. SSL/TLS with Certbot
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

### 4. Performance Tuning
- Use multiple workers: `uvicorn src.api_server:app --workers 4`
- Enable response compression
- Implement Redis caching for scraper results
- Use CDN for static assets

### 5. Monitoring
- Setup logging to file/service
- Use monitoring service (New Relic, DataDog)
- Implement health checks
- Setup alerts for failures

## 📊 Scaling Considerations

### Horizontal Scaling:
- Use load balancer (HAProxy, Nginx)
- Deploy multiple instances
- Share cache with Redis
- Use message queue for heavy operations

### Vertical Scaling:
- Increase server resources
- Optimize Playwright browser pool
- Tune Python garbage collection
- Use PyPy for better performance

## 🔒 Security Checklist

- [ ] Restrict CORS origins
- [ ] Implement rate limiting
- [ ] Add authentication/authorization
- [ ] Use HTTPS only
- [ ] Sanitize user inputs
- [ ] Hide error details in production
- [ ] Rotate API keys regularly
- [ ] Setup firewall rules
- [ ] Enable security headers
- [ ] Regular dependency updates

## 🐛 Troubleshooting

### Common Issues:

1. **Playwright browsers not installing:**
```bash
# Install system dependencies
playwright install-deps chromium
```

2. **Memory issues with scrapers:**
- Increase Docker memory limit
- Reduce concurrent scraping
- Implement browser recycling

3. **Slow scraping performance:**
- Ensure `SCRAPER_HEADLESS=true`
- Use browser connection pooling
- Implement result caching

4. **API timeouts:**
- Increase timeout settings
- Implement background jobs
- Use webhook callbacks for long operations

## 📈 Performance Metrics

Monitor these key metrics:
- API response time (target: <500ms)
- Scraper success rate (target: >95%)
- Memory usage (target: <2GB)
- CPU usage (target: <70%)
- Error rate (target: <1%)

## 🚦 Health Checks

The API provides health endpoints:
- `/api/health` - Basic health check
- `/api/status` - Detailed status with service states

## 📝 Maintenance

### Regular tasks:
- Update dependencies monthly
- Rotate logs weekly
- Monitor disk usage
- Check scraper effectiveness
- Review error logs

### Backup strategy:
- Backup environment variables
- Version control for code
- Document API changes
- Export usage metrics

---

For support, check the main README or open an issue on GitHub.