# FairResolve AI 

AI-assisted dispute and chargeback resolution platform with explainable evidence analysis, fairness scoring, and transparent decision-making.

## Features

- Customer, Merchant, and Investigator role-based workflows
- JWT authentication and protected APIs
- Customer transaction and purchase management
- UPI, Credit Card, and Debit Card transaction support
- Customer dispute creation directly from purchases
- Multiple dispute types:
  - Product Not Received
  - Wrong Product Received
  - Product Damaged
  - Duplicate Charge
- Evidence upload and document processing
- Gemini-powered AI evidence understanding
- Rule-based fallback when Gemini is unavailable
- Structured fact extraction from evidence
- Evidence relevance filtering and duplicate-evidence protection
- Customer vs. merchant evidence comparison
- Contradiction detection
- Explainable fairness and evidence scoring
- AI-assisted decision explanations
- Investigator review and case resolution
- Audit trail for dispute activity
- Interactive Swagger/OpenAPI documentation
- Responsive React frontend

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
