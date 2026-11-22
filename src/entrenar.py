"""Entrena una regresion logistica para predecir churn y guarda el modelo.

Uso:
    python src/entrenar.py                               (usa el CSV real de Kaggle)
    python src/entrenar.py data/procesado/telco_limpio.csv   (asi lo corre DVC)
"""
import json
import sys
from pathlib import Path

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.datos import leer_y_limpiar, ruta_datos  # noqa: E402
from src.prediccion import (CARPETA_MODELOS, COLUMNAS, COLUMNAS_CAT,  # noqa: E402
                            COLUMNAS_NUM, RUTA_MODELO)


def cargar_datos(ruta):
    df = leer_y_limpiar(ruta)
    X = df[COLUMNAS]
    y = (df["Churn"] == "Yes").astype(int)
    return X, y


def construir_modelo():
    preprocesamiento = ColumnTransformer([
        ("num", StandardScaler(), COLUMNAS_NUM),
        ("cat", OneHotEncoder(handle_unknown="ignore"), COLUMNAS_CAT),
    ])
    return Pipeline([
        ("prep", preprocesamiento),
        ("modelo", LogisticRegression(max_iter=1000)),
    ])


def calcular_metricas(y_real, pred, prob):
    return {
        "accuracy": round(accuracy_score(y_real, pred), 4),
        "precision": round(precision_score(y_real, pred), 4),
        "recall": round(recall_score(y_real, pred), 4),
        "f1": round(f1_score(y_real, pred), 4),
        "roc_auc": round(roc_auc_score(y_real, prob), 4),
    }


def main():
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else ruta_datos()
    X, y = cargar_datos(ruta)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    modelo = construir_modelo()
    modelo.fit(X_train, y_train)

    pred = modelo.predict(X_test)
    prob = modelo.predict_proba(X_test)[:, 1]
    metricas = calcular_metricas(y_test, pred, prob)

    CARPETA_MODELOS.mkdir(exist_ok=True)
    joblib.dump(modelo, RUTA_MODELO)
    with open(CARPETA_MODELOS / "metricas.json", "w") as f:
        json.dump(metricas, f, indent=2)

    print("Datos usados:", ruta)
    print("Modelo guardado en", RUTA_MODELO)
    print("Metricas:")
    for nombre, valor in metricas.items():
        print(f"  {nombre}: {valor}")
    print("Matriz de confusion (filas = real, columnas = prediccion):")
    print(confusion_matrix(y_test, pred))


if __name__ == "__main__":
    main()
