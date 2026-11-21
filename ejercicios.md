# Ejercicios - Practica 8 CI/CD

Haz los ejercicios en orden. En cada uno toma captura de lo que se pide.

### Ejercicio 1. Correr todo en local
Sigue los pasos 1 a 3 del README. Captura: la terminal con `8 passed` y el formulario
dando una prediccion.

### Ejercicio 2. Docker en local
Construye la imagen y corre el contenedor (paso 4). Captura: `docker ps` mostrando el
contenedor y el navegador con la app.

### Ejercicio 3. Primer workflow en verde
Sube el proyecto a GitHub (paso 5). Captura: la pestaña Actions con los dos jobs en verde.

### Ejercicio 4. Romper el pipeline a proposito
En `tests/test_modelo.py` cambia la accuracy minima de `0.70` a `0.99`, haz commit y push.
- Que job falla y en que paso?
- Se ejecuto el job `publicar`? Por que?

Regresa el valor a `0.70` y vuelve a subirlo hasta que quede en verde.

### Ejercicio 5. Agregar pruebas nuevas
Crea `tests/test_api_extra.py` con dos pruebas:
- Que la API rechace (codigo 422) un cliente con `tenure` negativo.
- Que la API rechace un cliente al que le falta el campo `Contract`.

Corre `pytest -v` en local y despues sube el cambio.

### Ejercicio 6. Revisar el estilo del codigo
Agrega al workflow, antes de entrenar el modelo, un paso que instale `ruff` y ejecute
`ruff check src app tests`. Si marca errores, corrigelos.

### Ejercicio 7. Usar la imagen publicada
Entra a Packages en tu perfil de GitHub, copia el comando `docker pull` de tu imagen y
corre la app desde esa imagen (no desde la que construiste en local).

### Preguntas
1. Con tus palabras, cual es la diferencia entre CI y CD en este proyecto?
2. Por que el Dockerfile vuelve a entrenar el modelo?
3. Que pasaria si alguien sube un cambio que baja la accuracy a 0.60?
