# Production Deployment & Docker Guide

## 1. Docker Compose One-Command Launch
```bash
# Build and start all services (Backend + Frontend + Database)
docker compose up --build -d
```

### Services Started:
- **Backend API**: `http://localhost:8000` (Healthcheck at `/health`)
- **Frontend Dashboard**: `http://localhost:3000`

---

## 2. Standalone Production Deployment

### Backend Service (FastAPI)
```bash
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Web UI (Nginx / Static Hosting)
```bash
cd frontend
npm install
npm run build
# Deploy `frontend/dist/` to Nginx, AWS S3 / CloudFront, or Cloudflare Pages
```
