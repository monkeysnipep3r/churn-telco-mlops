"""DAG de Airflow: pipeline semanal del modelo de churn.

preparar_datos -> entrenar_modelo -> validar_modelo -> monitorear_drift

El proyecto completo se monta dentro del contenedor en /opt/airflow/proyecto
(ver docker-compose.airflow.yml).
"""
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

CARPETA = "cd /opt/airflow/proyecto && "

with DAG(
    dag_id="pipeline_churn_telco",
    description="Prepara datos, entrena, valida y monitorea el modelo de churn",
    start_date=datetime(2026, 11, 1),
    schedule="@weekly",
    catchup=False,
    tags=["mlops", "churn"],
) as dag:

    preparar_datos = BashOperator(
        task_id="preparar_datos",
        bash_command=CARPETA + "python src/preparar.py",
    )

    entrenar_modelo = BashOperator(
        task_id="entrenar_modelo",
        bash_command=CARPETA + "python src/entrenar.py data/procesado/telco_limpio.csv",
    )

    validar_modelo = BashOperator(
        task_id="validar_modelo",
        bash_command=CARPETA + "python src/validar_modelo.py",
    )

    monitorear_drift = BashOperator(
        task_id="monitorear_drift",
        bash_command=CARPETA + "python src/monitoreo.py",
    )

    preparar_datos >> entrenar_modelo >> validar_modelo >> monitorear_drift
