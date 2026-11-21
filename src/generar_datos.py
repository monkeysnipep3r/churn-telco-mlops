"""Genera un CSV sintetico con las mismas columnas del dataset Telco Customer Churn.

Sirve para que la practica funcione sin descargar nada. Si tienes el CSV real de
Kaggle (WA_Fn-UseC_-Telco-Customer-Churn.csv) puedes usarlo en su lugar.
"""
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent


def generar(n=1500, semilla=42):
    rng = np.random.default_rng(semilla)

    contrato = rng.choice(["Month-to-month", "One year", "Two year"], n, p=[0.55, 0.21, 0.24])
    internet = rng.choice(["DSL", "Fiber optic", "No"], n, p=[0.34, 0.44, 0.22])
    pago = rng.choice(
        ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
        n, p=[0.34, 0.23, 0.22, 0.21],
    )
    senior = rng.choice([0, 1], n, p=[0.84, 0.16])
    paperless = rng.choice(["Yes", "No"], n, p=[0.59, 0.41])
    tenure = rng.integers(0, 73, n)

    base = np.where(internet == "Fiber optic", 80, np.where(internet == "DSL", 55, 22))
    mensual = np.round(base + rng.normal(0, 10, n), 2).clip(18, 120)
    total = np.round(mensual * np.maximum(tenure, 1) + rng.normal(0, 50, n), 2).clip(18, None)

    # Probabilidad de churn: sube con contrato mensual, fibra, cheque electronico
    # y baja con la antiguedad
    z = (-1.2
         + 1.6 * (contrato == "Month-to-month")
         - 1.0 * (contrato == "Two year")
         + 0.7 * (internet == "Fiber optic")
         + 0.6 * (pago == "Electronic check")
         + 0.4 * senior
         + 0.3 * (paperless == "Yes")
         - 0.04 * tenure)
    prob = 1 / (1 + np.exp(-z))
    churn = np.where(rng.random(n) < prob, "Yes", "No")

    def si_no(p):
        return rng.choice(["Yes", "No"], n, p=[p, 1 - p])

    df = pd.DataFrame({
        "customerID": [f"{i:04d}-SINT" for i in range(n)],
        "gender": rng.choice(["Male", "Female"], n),
        "SeniorCitizen": senior,
        "Partner": si_no(0.48),
        "Dependents": si_no(0.30),
        "tenure": tenure,
        "PhoneService": si_no(0.90),
        "MultipleLines": si_no(0.42),
        "InternetService": internet,
        "OnlineSecurity": si_no(0.29),
        "OnlineBackup": si_no(0.34),
        "DeviceProtection": si_no(0.34),
        "TechSupport": si_no(0.29),
        "StreamingTV": si_no(0.38),
        "StreamingMovies": si_no(0.39),
        "Contract": contrato,
        "PaperlessBilling": paperless,
        "PaymentMethod": pago,
        "MonthlyCharges": mensual,
        "TotalCharges": total,
        "Churn": churn,
    })
    return df


if __name__ == "__main__":
    salida = RAIZ / "data" / "telco_muestra.csv"
    df = generar()
    df.to_csv(salida, index=False)
    print(f"Archivo creado: {salida} ({len(df)} filas)")
