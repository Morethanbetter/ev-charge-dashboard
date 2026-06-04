# EV Charge Dashboard

Visual data monitoring dashboard for EV charging data analysis.

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + ECharts
- **Backend**: FastAPI + SQLAlchemy (async) + SQLite/PostgreSQL
- **Deployment**: Docker + Nginx + Railway

## Quick Start

### Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Docker Deployment

```bash
cd backend
docker-compose up --build -d
```

Default admin: `admin` / `admin123`

### Railway Deployment

Push to GitHub and connect to Railway. The backend includes `railway.toml` for one-click deployment.

## API

- Health check: `GET /api/v1/health`
- Auth: `POST /api/v1/auth/login`
- Files: Upload and manage CSV/Excel data files

## License

MIT
