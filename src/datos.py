"""Funciones para encontrar y leer los datos de Telco.

Los datos reales de Kaggle se versionan con DVC y no se suben a GitHub.
Por eso, si el CSV real no esta (por ejemplo en GitHub Actions), se usa
la muestra data/telco_muestra.csv que si esta en el repositorio.
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
CSV_REAL = RAIZ / "data" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
CSV_MUESTRA = RAIZ / "data" / "telco_muestra.csv"
CSV_LIMPIO = RAIZ / "data" / "procesado" / "telco_limpio.csv"


def ruta_datos():
    if CSV_REAL.exists():
        return CSV_REAL
    print("No se encontro el CSV real, se usan los datos de muestra")
    return CSV_MUESTRA


def leer_y_limpiar(ruta):
    df = pd.read_csv(ruta)
    # En el CSV real TotalCharges trae espacios en blanco, por eso se convierte a numero
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df = df.dropna(subset=["TotalCharges"])
    return df
