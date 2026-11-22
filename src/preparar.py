"""Primera etapa del pipeline: limpia los datos y los guarda en data/procesado/.

Uso:
    python src/preparar.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.datos import CSV_LIMPIO, leer_y_limpiar, ruta_datos  # noqa: E402


def main():
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else ruta_datos()
    filas_originales = len(pd.read_csv(ruta))

    df = leer_y_limpiar(ruta)
    df = df.drop(columns=["customerID"])

    CSV_LIMPIO.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_LIMPIO, index=False)

    print("Datos leidos de:", ruta)
    print("Filas originales:", filas_originales)
    print("Filas eliminadas por TotalCharges vacio:", filas_originales - len(df))
    print("Filas finales:", len(df))
    print("Archivo guardado en:", CSV_LIMPIO)


if __name__ == "__main__":
    main()
