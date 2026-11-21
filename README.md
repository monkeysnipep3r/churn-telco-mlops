# Practica 8 - CI/CD con GitHub Actions

En esta practica ya tienes una aplicacion hecha: una API en FastAPI que predice si un
cliente de una telefonica se va a ir (churn). La idea no es programar la app, sino
aprender a automatizar las pruebas (CI) y la publicacion de la imagen Docker (CD).

## Que trae el proyecto

```
08_cicd_telco/
├── app/main.py              API con FastAPI (/, /health, /predict)
├── app/static/index.html    Formulario para probar la API desde el navegador
├── src/entrenar.py          Entrena el modelo (regresion logistica)
├── src/prediccion.py        Carga el modelo y hace predicciones
├── src/generar_datos.py     Crea el CSV de ejemplo
├── data/telco_muestra.csv   Datos sinteticos con las columnas del dataset Telco
├── models/                  Modelo entrenado y sus metricas
├── tests/                   Pruebas automaticas con pytest
├── Dockerfile
├── .github/workflows/ci_cd.yml   Workflow de GitHub Actions
├── ejercicios.md            Lo que tienes que hacer
└── solucion_profesor/       Soluciones (no verlas antes de intentar)
```

Nota: los datos son sinteticos, para no tener que descargar nada. Si quieres usar el CSV
real de Kaggle, ponlo en `data/` y corre `python src/entrenar.py data/WA_Fn-UseC_-Telco-Customer-Churn.csv`.

## Lo que necesitas

- Python 3.11 o mas nuevo
- Git y una cuenta de GitHub
- Docker (Docker Desktop en Windows)
- VS Code

## 1. Preparar el entorno

Abre la carpeta del proyecto en VS Code (File > Open Folder) y abre una terminal
(Terminal > New Terminal).

**Windows (PowerShell):**
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Si PowerShell no te deja activar el venv, corre primero
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y responde que si.

**Linux:**
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Sabes que el venv esta activo porque aparece `(venv)` al inicio de la linea.

## 2. Entrenar y probar

```
python src/entrenar.py
pytest -v
```
Deben salir 8 pruebas en verde (`8 passed`).

## 3. Levantar la API

```
uvicorn app.main:app --reload
```
Abre en el navegador:
- http://localhost:8000 para el formulario
- http://localhost:8000/docs para la documentacion automatica de FastAPI

Para detenerla presiona `Ctrl + C`.

## 4. Probar con Docker

```
docker build -t churn-api .
docker run -p 8000:8000 churn-api
```
Y abre otra vez http://localhost:8000.

## 5. Subir a GitHub y ver el workflow

Crea un repositorio vacio en GitHub (sin README) y luego:
```
git init
git add .
git commit -m "Practica 8 CI/CD"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```
En GitHub entra a la pestaña **Actions** y revisa que los dos jobs (`pruebas` y
`publicar`) terminen en verde. La imagen publicada aparece en tu perfil, en **Packages**.

Despues sigue con `ejercicios.md`.
