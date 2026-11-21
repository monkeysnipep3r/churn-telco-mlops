FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Se vuelve a entrenar dentro de la imagen para que el modelo
# quede con la misma version de scikit-learn que se instalo arriba
RUN python src/entrenar.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
