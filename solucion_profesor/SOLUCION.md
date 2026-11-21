# Solucion - Practica 8

**Ejercicio 4.** Falla el job `pruebas` en el paso "Correr pruebas" (`test_accuracy_minima`).
El job `publicar` no corre porque tiene `needs: pruebas`: si las pruebas fallan, no se
publica ninguna imagen. Esa es la idea principal del CI/CD.

**Ejercicio 5.** Ver `tests/test_api_extra.py` en esta carpeta. FastAPI regresa 422
automaticamente porque el modelo `Cliente` tiene `Field(ge=0)` en tenure y todos los
campos son obligatorios.

**Ejercicio 6.** Ver `.github/workflows/ci_cd.yml` en esta carpeta, el paso
"Revisar estilo del codigo (ruff)".

**Ejercicio 7.**
```
docker pull ghcr.io/TU_USUARIO/TU_REPO:latest
docker run -p 8000:8000 ghcr.io/TU_USUARIO/TU_REPO:latest
```
Si el paquete es privado hay que hacer `docker login ghcr.io` con un token, o cambiar el
paquete a publico en su configuracion.

**Preguntas.**
1. CI: en cada push se instala todo, se entrena, se prueban el modelo y la API y se revisa
   que el contenedor arranque. CD: si todo eso pasa en `main`, la imagen se publica sola en GHCR.
2. Para que el modelo quede guardado con la misma version de scikit-learn que tiene la
   imagen. Si se usa un modelo hecho con otra version puede dar advertencias o errores.
3. La prueba `test_accuracy_minima` fallaria, el workflow quedaria en rojo y no se
   publicaria la imagen.
