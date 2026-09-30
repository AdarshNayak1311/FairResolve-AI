# FairResolve AI — Phase 1

Foundation for the CodeStreet 2026 dispute-resolution prototype.

## Phase 1 includes

- React + Vite frontend
- FastAPI backend
- PostgreSQL database
- SQLAlchemy ORM
- JWT authentication
- Customer / Merchant / Investigator roles
- Health endpoint
- Basic professional UI

## Requirements

- Node.js 18+
- Python 3.10+
- Docker Desktop

## 1. Start PostgreSQL

From the project root:

```bash
docker compose up -d
```

Check:

```bash
docker compose ps
```

## 2. Start backend

Open terminal:

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`.

Start API:

```bash
uvicorn app.main:app --reload
```

Backend:
http://localhost:8000

Swagger docs:
http://localhost:8000/docs

Health:
http://localhost:8000/api/health

## 3. Start frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:
http://localhost:5173

## Test

1. Open the frontend.
2. Create a customer account.
3. Log out.
4. Create a merchant account.
5. Log out.
6. Login again.
7. Backend authentication can also be tested from `/docs`.

## Important

This is a development prototype. Do not use the included database password or JWT secret in production.
