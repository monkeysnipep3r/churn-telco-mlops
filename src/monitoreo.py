"""Monitoreo del modelo: detecta data drift y revisa si bajo el desempeno.

Compara los datos con los que se entreno el modelo (referencia) contra un
lote de datos nuevos. Para cada variable:
  - numericas: prueba de Kolmogorov-Smirnov
  - categoricas: prueba chi-cuadrada
  - todas: PSI (Population Stability Index)
Se considera que hay drift si el p-valor es menor a 0.05.

Uso:
    python src/monitoreo.py
Genera:
    reports/drift_resultados.csv
    reports/metricas_monitoreo.json
    reports/drift_reporte.html   (abrirlo con doble clic)
"""
import base64
import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, ks_2samp

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.datos import leer_y_limpiar, ruta_datos  # noqa: E402
from src.entrenar import calcular_metricas  # noqa: E402
from src.prediccion import (COLUMNAS, COLUMNAS_CAT, COLUMNAS_NUM, RAIZ,  # noqa: E402
                            cargar_modelo)

LOTE_NUEVO = RAIZ / "data" / "nuevos" / "lote_nuevo.csv"
CARPETA_REPORTES = RAIZ / "reports"
ALFA = 0.05


def psi(referencia, actual, numerica, bins=10):
    """Population Stability Index. Menos de 0.1 es estable, mas de 0.25 es un cambio fuerte."""
    if numerica:
        cortes = np.unique(np.quantile(referencia, np.linspace(0, 1, bins + 1)))
        cortes[0], cortes[-1] = -np.inf, np.inf
        ref = pd.cut(referencia, cortes).value_counts(normalize=True, sort=False)
        act = pd.cut(actual, cortes).value_counts(normalize=True, sort=False)
    else:
        categorias = sorted(set(referencia) | set(actual))
        ref = referencia.value_counts(normalize=True).reindex(categorias, fill_value=0)
        act = actual.value_counts(normalize=True).reindex(categorias, fill_value=0)
    ref = np.clip(ref.values, 1e-4, None)
    act = np.clip(act.values, 1e-4, None)
    return float(np.sum((act - ref) * np.log(act / ref)))


def revisar_drift(referencia, actual):
    filas = []
    for col in COLUMNAS:
        numerica = col in COLUMNAS_NUM and col != "SeniorCitizen"  # es 0/1, se trata como categoria
        if numerica:
            prueba = "Kolmogorov-Smirnov"
            _, p = ks_2samp(referencia[col], actual[col])
        else:
            prueba = "Chi-cuadrada"
            tabla = pd.concat([
                referencia[col].value_counts(), actual[col].value_counts()
            ], axis=1).fillna(0)
            _, p, _, _ = chi2_contingency(tabla.T)
        filas.append({
            "variable": col,
            "tipo": "numerica" if numerica else "categorica",
            "prueba": prueba,
            "p_valor": round(float(p), 6),
            "psi": round(psi(referencia[col], actual[col], numerica), 4),
            "hay_drift": bool(p < ALFA),
        })
    return pd.DataFrame(filas)


def grafica_base64(referencia, actual, col):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5, 3.2))
    if col in COLUMNAS_NUM and col != "SeniorCitizen":
        ax.hist(referencia[col], bins=30, alpha=0.5, density=True, label="Entrenamiento")
        ax.hist(actual[col], bins=30, alpha=0.5, density=True, label="Lote nuevo")
    else:
        ref = referencia[col].value_counts(normalize=True)
        act = actual[col].value_counts(normalize=True).reindex(ref.index, fill_value=0)
        x = np.arange(len(ref))
        ax.bar(x - 0.2, ref.values, 0.4, label="Entrenamiento")
        ax.bar(x + 0.2, act.values, 0.4, label="Lote nuevo")
        ax.set_xticks(x)
        ax.set_xticklabels([str(i) for i in ref.index], rotation=20, fontsize=8)
    ax.set_title(col)
    ax.legend(fontsize=8)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=90)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def crear_html(resultados, metricas, referencia, actual):
    filas_tabla = ""
    for _, r in resultados.iterrows():
        color = "#f8d7da" if r["hay_drift"] else "#d4edda"
        filas_tabla += (f"<tr style='background:{color}'><td>{r['variable']}</td><td>{r['prueba']}</td>"
                        f"<td>{r['p_valor']}</td><td>{r['psi']}</td>"
                        f"<td>{'Si' if r['hay_drift'] else 'No'}</td></tr>")

    filas_met = ""
    for nombre in metricas["referencia"]:
        filas_met += (f"<tr><td>{nombre}</td><td>{metricas['referencia'][nombre]}</td>"
                      f"<td>{metricas['lote_nuevo'][nombre]}</td></tr>")

    graficas = "".join(
        f"<img src='data:image/png;base64,{grafica_base64(referencia, actual, c)}'>"
        for c in COLUMNAS
    )

    html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>Monitoreo de data drift</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 30px; }}
table {{ border-collapse: collapse; margin-bottom: 25px; }}
td, th {{ border: 1px solid #999; padding: 6px 12px; }}
th {{ background: #eee; }}
img {{ margin: 5px; border: 1px solid #ddd; }}
</style></head><body>
<h2>Monitoreo del modelo de churn (Telco)</h2>
<p>Datos de referencia: {len(referencia)} clientes con los que se entreno el modelo.<br>
Lote nuevo: {len(actual)} clientes. Nivel de significancia: {ALFA}.</p>

<h3>Desempeno del modelo</h3>
<table><tr><th>Metrica</th><th>Datos de referencia</th><th>Lote nuevo</th></tr>{filas_met}</table>

<h3>Deteccion de data drift</h3>
<p>Variables con drift: {int(resultados['hay_drift'].sum())} de {len(resultados)}</p>
<table><tr><th>Variable</th><th>Prueba</th><th>p-valor</th><th>PSI</th><th>Drift</th></tr>
{filas_tabla}</table>

<h3>Distribuciones</h3>
{graficas}
</body></html>"""
    (CARPETA_REPORTES / "drift_reporte.html").write_text(html, encoding="utf-8")


def main():
    if not LOTE_NUEVO.exists():
        print("No existe el lote nuevo. Ejecuta primero: python src/simular_lote_nuevo.py")
        sys.exit(1)

    referencia = leer_y_limpiar(ruta_datos())
    actual = leer_y_limpiar(LOTE_NUEVO)

    resultados = revisar_drift(referencia, actual)

    modelo = cargar_modelo()
    metricas = {}
    for nombre, df in [("referencia", referencia), ("lote_nuevo", actual)]:
        y = (df["Churn"] == "Yes").astype(int)
        pred = modelo.predict(df[COLUMNAS])
        prob = modelo.predict_proba(df[COLUMNAS])[:, 1]
        metricas[nombre] = calcular_metricas(y, pred, prob)
        metricas[nombre]["tasa_churn"] = round(float(y.mean()), 4)

    CARPETA_REPORTES.mkdir(exist_ok=True)
    resultados.to_csv(CARPETA_REPORTES / "drift_resultados.csv", index=False)
    with open(CARPETA_REPORTES / "metricas_monitoreo.json", "w") as f:
        json.dump(metricas, f, indent=2)
    crear_html(resultados, metricas, referencia, actual)

    print("Resultados de data drift:")
    print(resultados.to_string(index=False))
    print(f"\nVariables con drift: {int(resultados['hay_drift'].sum())} de {len(resultados)}")
    print("\nDesempeno del modelo:")
    print(pd.DataFrame(metricas).to_string())
    print("\nReporte guardado en", CARPETA_REPORTES / "drift_reporte.html")


if __name__ == "__main__":
    main()
