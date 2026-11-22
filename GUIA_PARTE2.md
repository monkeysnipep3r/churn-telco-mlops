# Parte 2: DVC, MLflow, Airflow y monitoreo

Todo se hace en la terminal de VS Code, dentro del proyecto y con el `(venv)` activado.

## 0. Instalar
```
pip install -r requirements-mlops.txt
```

## 1. DVC (seccion 2.2)
```
git rm --cached data/WA_Fn-UseC_-Telco-Customer-Churn.csv models/modelo.joblib
git commit -m "Los datos y el modelo pasan a DVC"
dvc init
python src/simular_lote_nuevo.py
dvc add data/WA_Fn-UseC_-Telco-Customer-Churn.csv
dvc add data/nuevos/lote_nuevo.csv
dvc remote add -d almacen ../dvc_almacen
dvc repro
dvc push
dvc dag
dvc metrics show
git add .
git commit -m "Versionado de datos y pipeline con DVC"
git push
```

## 2. MLflow (seccion 2.3)
```
python src/experimentos.py
mlflow ui --backend-store-uri sqlite:///mlflow.db
```
Abrir http://localhost:5000

## 3. Monitoreo (seccion 2.8)
`dvc repro` ya genera `reports/drift_reporte.html`. Abrirlo con doble clic.
Tambien se puede correr solo con `python src/monitoreo.py`.

## 4. Airflow (seccion 2.4)
```
docker compose -f docker-compose.airflow.yml up -d
docker compose -f docker-compose.airflow.yml exec airflow cat standalone_admin_password.txt
```
Abrir http://localhost:8080 (usuario admin), activar el DAG `pipeline_churn_telco` y ejecutarlo.
Para apagar: `docker compose -f docker-compose.airflow.yml down`
