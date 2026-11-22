"""Compara varios modelos con MLflow y registra el mejor en el Model Registry.

Uso:
    python src/experimentos.py
Despues, para ver los resultados:
    mlflow ui --backend-store-uri sqlite:///mlflow.db
y abrir http://localhost:5000
"""
import sys
from pathlib import Path

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.datos import CSV_LIMPIO, ruta_datos  # noqa: E402
from src.entrenar import calcular_metricas, cargar_datos  # noqa: E402
from src.prediccion import COLUMNAS_CAT, COLUMNAS_NUM, RAIZ  # noqa: E402

NOMBRE_EXPERIMENTO = "churn-telco"
NOMBRE_MODELO_REGISTRADO = "churn-telco-modelo"

MODELOS = {
    "regresion_logistica_C1": (LogisticRegression, {"C": 1.0, "max_iter": 1000}),
    "regresion_logistica_C01": (LogisticRegression, {"C": 0.1, "max_iter": 1000}),
    "arbol_decision": (DecisionTreeClassifier, {"max_depth": 5, "random_state": 42}),
    "random_forest": (RandomForestClassifier,
                      {"n_estimators": 200, "max_depth": 8, "random_state": 42}),
    "gradient_boosting": (GradientBoostingClassifier,
                          {"n_estimators": 150, "learning_rate": 0.1, "random_state": 42}),
}


def construir(clase, parametros):
    prep = ColumnTransformer([
        ("num", StandardScaler(), COLUMNAS_NUM),
        ("cat", OneHotEncoder(handle_unknown="ignore"), COLUMNAS_CAT),
    ])
    return Pipeline([("prep", prep), ("modelo", clase(**parametros))])


def main():
    ruta = CSV_LIMPIO if CSV_LIMPIO.exists() else ruta_datos()
    X, y = cargar_datos(ruta)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Se guarda todo en un archivo SQLite dentro del proyecto.
    # El Model Registry de MLflow necesita una base de datos, por eso no se usa la carpeta mlruns.
    mlflow.set_tracking_uri(f"sqlite:///{(RAIZ / 'mlflow.db').as_posix()}")
    mlflow.set_experiment(NOMBRE_EXPERIMENTO)

    resultados = []
    for nombre, (clase, parametros) in MODELOS.items():
        with mlflow.start_run(run_name=nombre) as run:
            modelo = construir(clase, parametros)
            modelo.fit(X_train, y_train)
            pred = modelo.predict(X_test)
            prob = modelo.predict_proba(X_test)[:, 1]
            metricas = calcular_metricas(y_test, pred, prob)

            mlflow.log_param("algoritmo", clase.__name__)
            mlflow.log_params(parametros)
            mlflow.log_param("datos", Path(ruta).name)
            mlflow.log_param("filas_entrenamiento", len(X_train))
            mlflow.log_metrics(metricas)
            mlflow.sklearn.log_model(modelo, "modelo", input_example=X_train.head(3))

            resultados.append((nombre, run.info.run_id, metricas))
            print(f"{nombre:25s} accuracy={metricas['accuracy']}  f1={metricas['f1']}  "
                  f"recall={metricas['recall']}  roc_auc={metricas['roc_auc']}")

    # El mejor modelo se elige por F1, porque importa encontrar a los clientes que se van
    mejor_nombre, mejor_run, mejores = max(resultados, key=lambda r: r[2]["f1"])
    print(f"\nMejor modelo por F1: {mejor_nombre} (f1={mejores['f1']})")

    version = mlflow.register_model(f"runs:/{mejor_run}/modelo", NOMBRE_MODELO_REGISTRADO)
    cliente = MlflowClient()
    cliente.set_registered_model_alias(NOMBRE_MODELO_REGISTRADO, "champion", version.version)
    print(f"Registrado como '{NOMBRE_MODELO_REGISTRADO}' version {version.version} "
          f"con el alias 'champion'")


if __name__ == "__main__":
    main()
