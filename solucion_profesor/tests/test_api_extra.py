# Solucion del ejercicio 5: copiar este archivo a la carpeta tests/
from fastapi.testclient import TestClient

from app.main import app

cliente_http = TestClient(app)

CLIENTE = {
    "tenure": 5, "MonthlyCharges": 85.0, "TotalCharges": 425.0, "SeniorCitizen": 0,
    "Contract": "Month-to-month", "InternetService": "Fiber optic",
    "PaymentMethod": "Electronic check", "PaperlessBilling": "Yes",
}


def test_tenure_negativo_se_rechaza():
    r = cliente_http.post("/predict", json=dict(CLIENTE, tenure=-3))
    assert r.status_code == 422


def test_falta_un_campo():
    incompleto = dict(CLIENTE)
    del incompleto["Contract"]
    r = cliente_http.post("/predict", json=incompleto)
    assert r.status_code == 422
