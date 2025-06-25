import pandas as pd
import streamlit as st
from pathlib import Path
import os

st.set_page_config(page_title="Tablas de Posiciones", layout="wide")

st.title("Visualización de Tablas de Posiciones y Resultados")

# Ajuste: usar ruta absoluta para outputs
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = Path(script_dir) / ".." / "outputs"
data_dir = data_dir.resolve()

if not data_dir.exists():
    st.error(f"No se encontró la carpeta de outputs en: {data_dir}")
    st.stop()

zonas = sorted([d.name for d in data_dir.iterdir() if d.is_dir()])
if not zonas:
    st.error("No hay zonas disponibles en outputs.")
    st.stop()

# Selects en línea
col1, col2, col3 = st.columns(3)
with col1:
    zona = st.selectbox("Zona", zonas, key="zona")

zona_path = data_dir / zona
grupos = [d.name for d in zona_path.iterdir() if d.is_dir()]

with col2:
    grupo = st.selectbox("Grupo", grupos if grupos else ["Sin grupo"], key="grupo") if grupos else None
    grupo_path = zona_path / grupo if grupo else None

if grupos:
    categorias = [d.name for d in grupo_path.iterdir() if d.is_dir()]
else:
    categorias = [d.name for d in zona_path.iterdir() if d.is_dir()]

with col3:
    categoria = st.selectbox("Categoría", categorias, key="categoria")

# Paths de tablas
if grupos and grupo:
    tabla_path = grupo_path / categoria / "tabla.csv"
else:
    tabla_path = zona_path / categoria / "tabla.csv"

general_path = zona_path / "tabla_general.csv"
categoria_general_path = zona_path / categoria / "tabla.csv"

# Mostrar tabla general de la zona
if general_path.exists():
    st.subheader(f"Tabla General de la Zona {zona}")
    tabla_general = pd.read_csv(general_path, index_col=0)
    st.dataframe(tabla_general)

# Mostrar tabla general de la categoría
if categoria_general_path.exists():
    st.subheader(f"Tabla General de la Categoría {categoria} en Zona {zona}")
    tabla_cat_general = pd.read_csv(categoria_general_path, index_col=0)
    st.dataframe(tabla_cat_general)

# Mostrar tabla de posiciones seleccionada
if not tabla_path.exists():
    st.error(f"No se encontró la tabla: {tabla_path}")
    st.stop()

tabla = pd.read_csv(tabla_path, index_col=0)
st.subheader(f"Tabla de posiciones - Zona: {zona} " + (f"- Grupo: {grupo}" if grupo else "") + f" - Categoría: {categoria}")
st.dataframe(tabla, use_container_width=True)

# Mostrar resultados de partidos para la selección actual
st.subheader("Resultados de partidos")
partidos_path = Path(script_dir) / ".." / "Data" / "partidos_2025.csv"
partidos_path = partidos_path.resolve()
if not partidos_path.exists():
    st.error(f"No se encontró el archivo de partidos: {partidos_path}")
    st.stop()

partidos = pd.read_csv(partidos_path, sep=";")

# Filtros según selección
filtro = (partidos['zona'] == zona) & (partidos['categoria'].str.upper() == categoria.upper())
if grupo and grupo != "Sin grupo":
    filtro &= (partidos['grupo'] == grupo)
partidos_filtrados = partidos[filtro]

# Interactividad: mostrar detalle de partidos al seleccionar club y tipo
st.markdown("### Ver detalle de partidos por club y tipo de resultado")
equipo_sel = st.selectbox("Equipo", tabla.index.tolist(), key="equipo_detalle")
tipo_sel = st.selectbox("Tipo de resultado", ["PG", "PP", "NP"], key="tipo_detalle")

def get_tooltip(equipo, tipo, partidos_filtrados):
    if tipo == 'PG':
        ganados = partidos_filtrados[(partidos_filtrados['local'] == equipo) & (partidos_filtrados['ptsL'] > partidos_filtrados['ptsV'])]
        ganados = pd.concat([ganados, partidos_filtrados[(partidos_filtrados['visitante'] == equipo) & (partidos_filtrados['ptsV'] > partidos_filtrados['ptsL'])]])
        return ganados
    if tipo == 'PP':
        perdidos = partidos_filtrados[(partidos_filtrados['local'] == equipo) & (partidos_filtrados['ptsL'] < partidos_filtrados['ptsV'])]
        perdidos = pd.concat([perdidos, partidos_filtrados[(partidos_filtrados['visitante'] == equipo) & (partidos_filtrados['ptsV'] < partidos_filtrados['ptsL'])]])
        return perdidos
    if tipo == 'NP':
        np = partidos_filtrados[((partidos_filtrados['local'] == equipo) & (partidos_filtrados['ptsL'] == 0)) | ((partidos_filtrados['visitante'] == equipo) & (partidos_filtrados['ptsV'] == 0))]
        return np
    return pd.DataFrame()

detalle = get_tooltip(equipo_sel, tipo_sel, partidos_filtrados)
if not detalle.empty:
    st.dataframe(detalle[["fecha", "local", "ptsL", "ptsV", "visitante"]])
else:
    st.info("No hay partidos para mostrar.")
