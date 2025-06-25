import pandas as pd
import streamlit as st
from pathlib import Path
import os
import re

st.set_page_config(page_title="FORMATIVAS FEBAMBA 2025", layout="wide")

st.title("TORNEO DE FORMATIVAS FEBAMBA 2025")

# Explicación de criterios de desempate y "No Presenta"
with st.expander("ℹ️ Criterios de desempate y definición de 'No Presenta'"):
    st.markdown('''
**Criterios de desempate (Art. 12 FeBAMBA/AFMB):**
1. Puntos obtenidos en los partidos jugados entre los equipos empatados.
2. Mayor diferencia de tantos a favor y en contra en los partidos entre los equipos empatados.
3. Mayor diferencia de tantos a favor y en contra en todos los partidos de la competición.
4. Mayor número de tantos a favor en todos los partidos de la competición.
5. Gol Average: cociente entre tantos a favor y tantos en contra (mayor es mejor).
6. Promedio.

**Definición de "No Presenta" (NP):**
- Se considera "No Presenta" cuando un equipo pierde 0-20, 20-0 o 0-0.
- En MINI y PREMINI, solo se suma 1 punto por presentación (no se cuentan PG/PP), y NP refleja los partidos no presentados.
- La categoría JUVENILES no se incluye en la tabla general.
''')

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

# Buscar grupos: solo los subdirectorios numéricos
zona_path = data_dir / zona
grupos = [d.name for d in zona_path.iterdir() if d.is_dir() and re.match(r'^\d+$', d.name)]

if grupos:
    with col2:
        grupo = st.selectbox("Grupo", grupos, key="grupo")
        grupo_path = zona_path / grupo
    categorias = [d.name for d in grupo_path.iterdir() if d.is_dir()]
else:
    grupo = None
    categorias = [d.name for d in zona_path.iterdir() if d.is_dir() and not re.match(r'^tablas generales$', d.name, re.IGNORECASE)]

with col3:
    categoria = st.selectbox("Categoría", categorias, key="categoria")

# Paths de tablas
if grupos and grupo:
    tabla_path = grupo_path / categoria / "tabla.csv"
else:
    tabla_path = zona_path / categoria / "tabla.csv"

# Carpeta tablas generales dentro de la zona
zona_tablas_generales = zona_path / "tablas generales"
zona_tablas_generales.mkdir(exist_ok=True)
categoria_general_path = zona_tablas_generales / f"{categoria}.csv"

# Si no existe, generarla concatenando las tablas de todos los grupos
if not categoria_general_path.exists() and grupos:
    tablas = []
    for grupo in grupos:
        path = zona_path / grupo / categoria / "tabla.csv"
        if path.exists():
            df = pd.read_csv(path)
            df['GRUPO'] = grupo
            tablas.append(df)
    if tablas:
        tabla_cat_general = pd.concat(tablas, ignore_index=True)
        # Ordenar por puntos, DP, PF
        tabla_cat_general = tabla_cat_general.sort_values(['puntos', 'DP', 'PF'], ascending=[False, False, False])
        tabla_cat_general.to_csv(categoria_general_path, index=False)

# Mostrar tabla de la categoría seleccionada (primer fila)
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
# Normalizar mayúsculas y espacios para evitar problemas de coincidencia
partidos['zona'] = partidos['zona'].astype(str).str.strip().str.upper()
partidos['categoria'] = partidos['categoria'].astype(str).str.strip().str.upper()
if 'grupo' in partidos.columns:
    partidos['grupo'] = partidos['grupo'].astype(str).str.strip()

zona_norm = zona.strip().upper()
categoria_norm = categoria.strip().upper()

filtro = (partidos['zona'] == zona_norm) & (partidos['categoria'] == categoria_norm)
if grupo:
    grupo_norm = grupo.strip()
    if 'grupo' in partidos.columns:
        filtro &= (partidos['grupo'] == grupo_norm)
partidos_filtrados = partidos[filtro]

# Interactividad: mostrar detalle de partidos al seleccionar club y tipo
equipo_sel = st.selectbox("Equipo", tabla.index.tolist(), key="equipo_detalle")
tipo_sel = st.selectbox("Tipo de resultado", ["Ganados", "Perdidos", "No Presenta"], key="tipo_detalle")

def get_tooltip(equipo, tipo, partidos_filtrados):
    if tipo == 'Ganados':
        ganados = partidos_filtrados[(partidos_filtrados['local'] == equipo) & (partidos_filtrados['ptsL'] > partidos_filtrados['ptsV'])]
        ganados = pd.concat([ganados, partidos_filtrados[(partidos_filtrados['visitante'] == equipo) & (partidos_filtrados['ptsV'] > partidos_filtrados['ptsL'])]])
        return ganados
    if tipo == 'Perdidos':
        perdidos = partidos_filtrados[(partidos_filtrados['local'] == equipo) & (partidos_filtrados['ptsL'] < partidos_filtrados['ptsV'])]
        perdidos = pd.concat([perdidos, partidos_filtrados[(partidos_filtrados['visitante'] == equipo) & (partidos_filtrados['ptsV'] < partidos_filtrados['ptsL'])]])
        return perdidos
    if tipo == 'No Presenta':
        np = partidos_filtrados[((partidos_filtrados['local'] == equipo) & (partidos_filtrados['ptsL'] == 0)) | ((partidos_filtrados['visitante'] == equipo) & (partidos_filtrados['ptsV'] == 0))]
        return np
    return pd.DataFrame()

detalle = get_tooltip(equipo_sel, tipo_sel, partidos_filtrados)

if not detalle.empty:
    st.dataframe(detalle[["fecha", "local", "ptsL", "ptsV", "visitante"]])
else:
    st.info("No hay partidos para mostrar.")


# Segunda fila: dos columnas, tabla general y tabla general de la categoría
colA, colB = st.columns(2)

# Tabla general de la zona
with colA:
    general_path = zona_path / "tabla_general.csv"
    if general_path.exists():
        st.subheader(f"Tabla General de la Zona {zona}")
        tabla_general = pd.read_csv(general_path, index_col=0)
        st.dataframe(tabla_general)

# Tabla general de la categoría
with colB:
    if categoria_general_path.exists():
        st.subheader(f"Tabla General de {categoria} - {zona}")
        tabla_cat_general = pd.read_csv(categoria_general_path, index_col=0)
        st.dataframe(tabla_cat_general)