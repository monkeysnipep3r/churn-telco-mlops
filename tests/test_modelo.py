import json

import pytest

from src.prediccion import RAIZ, RUTA_MODELO, cargar_modelo, predecir

CLIENTE = {
    "tenure": 5, "MonthlyCharges": 85.0, "TotalCharges": 425.0, "SeniorCitizen": 0,
    "Contract": "Month-to-month", "InternetService": "Fiber optic",
    "PaymentMethod": "Electronic check", "PaperlessBilling": "Yes",
}


@pytest.fixture(scope="module")
def modelo():
    return cargar_modelo()


def test_el_modelo_existe():
    assert RUTA_MODELO.exists()


def test_prediccion_tiene_formato_correcto(modelo):
    r = predecir(modelo, CLIENTE)
    assert 0 <= r["probabilidad_churn"] <= 1
    assert isinstance(r["churn"], bool)


def test_contrato_largo_baja_el_riesgo(modelo):
    largo = dict(CLIENTE, Contract="Two year")
    assert predecir(modelo, largo)["probabilidad_churn"] < predecir(modelo, CLIENTE)["probabilidad_churn"]


def test_accuracy_minima():
    with open(RAIZ / "models" / "metricas.json") as f:
        metricas = json.load(f)
    assert metricas["accuracy"] >= 0.70
