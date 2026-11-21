"""API de prediccion de churn hecha con FastAPI.

Para correrla (desde la carpeta del proyecto):
    uvicorn app.main:app --reload
"""
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from src.prediccion import cargar_modelo, predecir

VERSION = "1.0.0"
CARPETA_APP = Path(__file__).resolve().parent


class Cliente(BaseModel):
    tenure: int = Field(ge=0, le=100, description="Meses como cliente")
    MonthlyCharges: float = Field(ge=0)
    TotalCharges: float = Field(ge=0)
    SeniorCitizen: int = Field(ge=0, le=1)
    Contract: Literal["Month-to-month", "One year", "Two year"]
    InternetService: Literal["DSL", "Fiber optic", "No"]
    PaymentMethod: Literal[
        "Electronic check", "Mailed check",
        "Bank transfer (automatic)", "Credit card (automatic)",
    ]
    PaperlessBilling: Literal["Yes", "No"]


app = FastAPI(title="Prediccion de churn Telco", version=VERSION)
modelo = cargar_modelo()


@app.get("/", response_class=HTMLResponse)
def inicio():
    return (CARPETA_APP / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {"status": "ok", "version": VERSION}


@app.post("/predict")
def predict(cliente: Cliente):
    return predecir(modelo, cliente.model_dump())
