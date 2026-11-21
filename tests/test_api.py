from fastapi.testclient import TestClient

from app.main import app

cliente_http = TestClient(app)

CLIENTE = {
    "tenure": 5, "MonthlyCharges": 85.0, "TotalCharges": 425.0, "SeniorCitizen": 0,
    "Contract": "Month-to-month", "InternetService": "Fiber optic",
    "PaymentMethod": "Electronic check", "PaperlessBilling": "Yes",
}


def test_health():
    r = cliente_http.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_pagina_inicio():
    r = cliente_http.get("/")
    assert r.status_code == 200
    assert "Predecir" in r.text


def test_predict_valido():
    r = cliente_http.post("/predict", json=CLIENTE)
    assert r.status_code == 200
    assert "probabilidad_churn" in r.json()


def test_predict_dato_invalido():
    malo = dict(CLIENTE, Contract="Tres meses")
    r = cliente_http.post("/predict", json=malo)
    assert r.status_code == 422
