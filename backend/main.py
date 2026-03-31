"""
FastAPI Backend for Medical Diagnostic Reasoning System.
=========================================================
Provides REST API endpoints for the Bayesian Network-based
medical diagnostic system.

Endpoints:
    GET  /                  - Health check
    GET  /api/symptoms      - List all available symptoms
    GET  /api/diseases       - List all diseases in the model
    GET  /api/risk-factors   - List all risk factors
    GET  /api/network        - Get network structure info
    POST /api/diagnose       - Run diagnosis with given symptoms
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import os

from backend.bayesian_network import BayesianNetwork
from backend.knowledge_base import (
    DISEASES, SYMPTOMS, RISK_FACTORS,
    PRIOR_PROBABILITIES, SENSITIVITY, _DISEASE_ORDER
)

# =============================================================================
# App Configuration
# =============================================================================

app = FastAPI(
    title="Medical Diagnostic Reasoning System",
    description=(
        "Hệ thống Chuẩn đoán Y khoa Thông minh sử dụng "
        "Mạng Bayesian và thuật toán Variable Elimination. "
        "Focused on Acute Respiratory Inflammation & Fever Syndrome."
    ),
    version="1.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# =============================================================================
# Request/Response Models
# =============================================================================

class DiagnoseRequest(BaseModel):
    """Request body for the diagnose endpoint."""
    symptoms: dict[str, bool] = Field(
        ...,
        description="Mapping of symptom name to True/False",
        examples=[{"Fever": True, "Cough": True, "Runny_Nose": False}]
    )
    risk_factors: Optional[list[str]] = Field(
        default=None,
        description="Optional list of active risk factor names",
        examples=[["Smoking", "Elderly"]]
    )


class DiagnoseResult(BaseModel):
    """Response body for the diagnose endpoint."""
    diagnoses: list[dict]
    evidence_used: list[str]
    most_likely: str
    most_likely_vi: str
    risk_factors: list[str]
    num_evidence: int
    num_diseases: int = 10


class SymptomInfo(BaseModel):
    """Information about a symptom."""
    name: str
    name_vi: str
    description: str
    type: str


class DiseaseInfo(BaseModel):
    """Information about a disease."""
    name: str
    name_vi: str
    description: str
    description_vi: str
    icd10: str
    category: str
    prior_probability: float


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Serve the frontend or return health check."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "healthy",
        "service": "Medical Diagnostic Reasoning System",
        "version": "1.0.0",
    }


@app.get("/api/symptoms", response_model=list[SymptomInfo])
async def get_symptoms():
    """Return all available symptoms that can be used as evidence."""
    result = []
    for name, info in SYMPTOMS.items():
        result.append(SymptomInfo(
            name=name,
            name_vi=info["name_vi"],
            description=info["description"],
            type=info["type"],
        ))
    return result


@app.get("/api/diseases", response_model=list[DiseaseInfo])
async def get_diseases():
    """Return all diseases in the diagnostic model."""
    result = []
    for name, info in DISEASES.items():
        result.append(DiseaseInfo(
            name=name,
            name_vi=info["name_vi"],
            description=info["description"],
            description_vi=info.get("description_vi", ""),
            icd10=info["icd10"],
            category=info["category"],
            prior_probability=PRIOR_PROBABILITIES[name],
        ))
    return result


@app.get("/api/risk-factors")
async def get_risk_factors():
    """Return all available risk factors."""
    result = []
    for name, info in RISK_FACTORS.items():
        result.append({
            "name": name,
            "name_vi": info["name_vi"],
            "description": info["description"],
        })
    return result


@app.get("/api/network")
async def get_network():
    """Return the Bayesian Network structure for visualization."""
    bn = BayesianNetwork()
    info = bn.get_network_info()

    # Add sensitivity data for visualization
    sensitivity_matrix = {}
    for symptom, values in SENSITIVITY.items():
        sensitivity_matrix[symptom] = {
            disease: val
            for disease, val in zip(_DISEASE_ORDER, values)
        }

    info["sensitivity_matrix"] = sensitivity_matrix
    return info


@app.post("/api/diagnose", response_model=DiagnoseResult)
async def diagnose(request: DiagnoseRequest):
    """
    Run medical diagnosis based on observed symptoms.

    Takes a set of symptoms (True/False) and optional risk factors,
    then computes posterior probabilities for each disease using
    Variable Elimination on the Bayesian Network.
    """
    # Validate symptoms
    valid_symptoms = set(SYMPTOMS.keys())
    invalid = set(request.symptoms.keys()) - valid_symptoms
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown symptoms: {invalid}. Valid: {valid_symptoms}"
        )

    # Validate risk factors
    if request.risk_factors:
        valid_rf = set(RISK_FACTORS.keys())
        invalid_rf = set(request.risk_factors) - valid_rf
        if invalid_rf:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown risk factors: {invalid_rf}. Valid: {valid_rf}"
            )

    # Build network and run diagnosis
    try:
        bn = BayesianNetwork(risk_factors=request.risk_factors)
        result = bn.diagnose(
            observed_symptoms=request.symptoms,
            risk_factors=request.risk_factors,
        )
        return DiagnoseResult(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Diagnosis error: {str(e)}"
        )


# =============================================================================
# Run with: uvicorn backend.main:app --reload --port 8000
# =============================================================================
