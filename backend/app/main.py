from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routes_auth import router as auth_router
from .routes_cards import router as cards_router
from .routes_transactions import router as transactions_router
from .routes_disputes import router as disputes_router
from .routes_evidence import router as evidence_router
from .routes_audit import router as audit_router
from .routes_uploads import router as uploads_router
from .routes_analysis import router as analysis_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FairResolve AI API",
    version="0.1.0",
    description="AI-assisted, explainable dispute resolution platform with evidence analysis, fair weighting, and auditability.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(cards_router)
app.include_router(transactions_router)
app.include_router(disputes_router)
app.include_router(evidence_router)
app.include_router(audit_router)
app.include_router(uploads_router)
app.include_router(analysis_router)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "fairresolve-api"}
