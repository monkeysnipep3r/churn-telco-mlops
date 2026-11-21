"""Funciones para cargar el modelo y hacer predicciones.

La API (app/main.py) y las pruebas (tests/) usan este archivo.
"""
from pathlib import Path

import joblib
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RUTA_MODELO = RAIZ / "models" / "modelo.joblib"

COLUMNAS_NUM = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]
COLUMNAS_CAT = ["Contract", "InternetService", "PaymentMethod", "PaperlessBilling"]
COLUMNAS = COLUMNAS_NUM + COLUMNAS_CAT

UMBRAL = 0.5


def cargar_modelo(ruta=RUTA_MODELO):
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontro el modelo en {ruta}. Ejecuta primero: python src/entrenar.py"
        )
    return joblib.load(ruta)


def predecir(modelo, cliente):
    """Recibe un diccionario con los datos de un cliente y regresa la prediccion."""
    df = pd.DataFrame([cliente])[COLUMNAS]
    prob = float(modelo.predict_proba(df)[0, 1])
    return {
        "probabilidad_churn": round(prob, 4),
        "churn": prob >= UMBRAL,
    }
