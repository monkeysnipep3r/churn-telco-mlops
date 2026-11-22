"""Crea un "lote nuevo" de clientes para probar el monitoreo de data drift.

Se toman 1500 clientes reales del mismo dataset, pero dando mas probabilidad
a clientes con contrato mensual, fibra optica, cheque electronico y poca
antiguedad. Asi se imita un cambio en el tipo de clientes que llegan
(por ejemplo, despues de una promocion de fibra optica con contrato mensual).

Uso:
    python src/simular_lote_nuevo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.datos import leer_y_limpiar, ruta_datos  # noqa: E402
from src.prediccion import RAIZ  # noqa: E402

SALIDA = RAIZ / "data" / "nuevos" / "lote_nuevo.csv"


def main():
    df = leer_y_limpiar(ruta_datos())

    peso = (1
            + 2.0 * (df["Contract"] == "Month-to-month")
            + 1.5 * (df["InternetService"] == "Fiber optic")
            + 1.0 * (df["PaymentMethod"] == "Electronic check")
            + 1.0 * (df["tenure"] < 12))
    lote = df.sample(n=1500, weights=peso, random_state=7)

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    lote.to_csv(SALIDA, index=False)
    print(f"Lote nuevo guardado en {SALIDA} ({len(lote)} clientes)")
    print(f"Churn en datos originales: {(df['Churn'] == 'Yes').mean():.1%}")
    print(f"Churn en el lote nuevo:    {(lote['Churn'] == 'Yes').mean():.1%}")


if __name__ == "__main__":
    main()
