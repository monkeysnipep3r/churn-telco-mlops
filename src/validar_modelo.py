"""Revisa que el modelo recien entrenado cumpla una accuracy minima.

Si no la cumple, termina con error para que el pipeline (Airflow) se detenga.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.prediccion import CARPETA_MODELOS  # noqa: E402

ACCURACY_MINIMA = 0.70


def main():
    with open(CARPETA_MODELOS / "metricas.json") as f:
        metricas = json.load(f)
    print("Metricas del modelo:", metricas)
    if metricas["accuracy"] < ACCURACY_MINIMA:
        print(f"El modelo NO pasa: accuracy menor a {ACCURACY_MINIMA}")
        sys.exit(1)
    print(f"El modelo pasa la validacion (accuracy >= {ACCURACY_MINIMA})")


if __name__ == "__main__":
    main()
