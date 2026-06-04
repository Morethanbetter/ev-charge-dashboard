# EV Charge Dashboard

Visual data monitoring dashboard for EV charging data analysis.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?templateUrl=https://github.com/Morethanbetter/ev-charge-dashboard)

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + ECharts
- **Backend**: FastAPI + SQLAlchemy (async) + SQLite/PostgreSQL
- **Deployment**: Docker + Nginx + Railway

## Quick Start

### One-Click Deploy (Recommended)

Click the "Deploy on Railway" button above, or visit:
https://railway.app/new/template?templateUrl=https://github.com/Morethanbetter/ev-charge-dashboard

**Required Environment Variables:**
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Auto-set by Railway PostgreSQL plugin |
| `SECRET_KEY` | JWT secret key | `changeme-production-secret-key` |
| `PORT` | Application port | `8000` (auto-set by Railway) |

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

## API

- Health check: `GET /api/v1/health`
- Auth: `POST /api/v1/auth/login`
- Files: Upload and manage CSV/Excel data files

## License

MIT
