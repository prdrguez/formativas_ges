import pandas as pd
from glob import glob
import sys
import os

# Agrega el directorio padre al path de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.open_csv import leer_csv_con_encoding_detectado

# === Configuración ===
columnas_clave = ["local", "visitante", "categoria", "fase", "ronda", "nivel", "zona", "grupo",  "fecha"]
path_archivos = "data/procesada/19-24.csv"
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

df_total = leer_csv_con_encoding_detectado(path_archivos)

# === Filtrado de partidos inválidos ===
def es_valido(row):
    campos = [row["fase"], row["ronda"], row["nivel"], row["zona"]]
    return all(c and isinstance(c, str) and c.strip().upper() != "DESCONOCIDO" for c in campos)

df_total["valido"] = df_total.apply(es_valido, axis=1)

df_validos = df_total[df_total["valido"]].copy()
df_invalidos = df_total[~df_total["valido"]].copy()

# Guardar log de inválidos
df_invalidos.to_csv(os.path.join(output_dir, "partidos_invalidos_log.csv"), index=False)

columnas_comunes = ["anio", "categoria", "fase", "ronda", "nivel", "zona", "grupo"]

df_local = df_validos[columnas_comunes + ["local"]].rename(columns={"local": "tira"})
df_visitante = df_validos[columnas_comunes + ["visitante"]].rename(columns={"visitante": "tira"})

df_final = pd.concat(
    [
        df_local, 
        df_visitante
    ], 
    axis=0
).sort_values(by=["anio", "categoria", "fase", "ronda", "zona", "grupo", "nivel"], ignore_index=True)


resumen = (
    df_final[df_final["fase"] == "Fase Regular"].groupby(["anio", "ronda", "nivel", "zona", "grupo"])
    .agg(
        cantidad_tiras=("tira", "nunique"),
        equipos=("tira", lambda x: ", ".join(sorted(x.unique())))
    )
    .reset_index()
    .sort_values(["anio", "zona", "nivel", "grupo"])
)

resumen.to_csv(os.path.join(output_dir, "resumen_estructura_por_anio.csv"), index=False)
print("✅ Estructura del torneo guardada en:", os.path.join(output_dir, "resumen_estructura_por_anio.csv"))