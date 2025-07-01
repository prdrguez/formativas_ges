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

# Visualización: cantidad de partidos por categoría y región según diferencia de puntos
st.header("Distribución de partidos por diferencia de puntos")

# Selector de región (zona)
region_sel = st.selectbox("Filtrar por región (zona)", zonas, key="region_dif")

# Filtrar partidos por región seleccionada
partidos_region = partidos[partidos['zona'].str.upper() == region_sel.strip().upper()]

# Definir los bins de diferencia (más detallados)
bins = [-float('inf'), 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, float('inf')]
labels = [
    'Menos de 5 pts',
    '5-10 pts',
    '10-20 pts',
    '20-30 pts',
    '30-40 pts',
    '40-50 pts',
    '50-60 pts',
    '60-70 pts',
    '70-80 pts',
    '80-90 pts',
    '90-100 pts',
    'Más de 100 pts'
]

partidos_region = partidos_region.copy()
partidos_region['diferencia'] = (partidos_region['ptsL'] - partidos_region['ptsV']).abs()
partidos_region['rango_dif'] = pd.cut(partidos_region['diferencia'], bins=bins, labels=labels, right=False)

# Agrupar por categoría y rango de diferencia
conteo = partidos_region.groupby(['categoria', 'rango_dif']).size().unstack(fill_value=0)
# Ordenar las columnas (rangos) de menor a mayor diferencia
conteo = conteo[labels]
# Calcular promedios excluyendo PREMINI
categorias_prom = [cat for cat in conteo.index if cat.strip().upper() != 'PREMINI']
promedios_categoria = partidos_region[~partidos_region['categoria'].str.strip().str.upper().eq('PREMINI')].groupby('categoria')['diferencia'].mean().reindex(categorias_prom)
promedios_categoria = promedios_categoria.round(2).rename('Promedio Dif. Pts')
conteo_prom = conteo.copy()
conteo_prom['Promedio Dif. Pts'] = None
conteo_prom.loc[categorias_prom, 'Promedio Dif. Pts'] = promedios_categoria
st.dataframe(conteo_prom)


# Mostrar gráfico de barras apiladas ordenado de menor a mayor diferencia
import plotly.express as px

# Agregar columna con listado de partidos por categoría y rango de diferencia
partidos_region['info_partido'] = partidos_region.apply(
    lambda x: f"{x['local']} {x['ptsL']}-{x['ptsV']} {x['visitante']}", axis=1)

# Agrupar para tooltip
tooltip_df = partidos_region.groupby(['categoria', 'rango_dif'])['info_partido'].apply(lambda x: '<br>'.join(x)).reset_index()
conteo_reset = conteo.reset_index().melt(id_vars='categoria', var_name='Diferencia', value_name='Cantidad')
conteo_reset = conteo_reset.merge(tooltip_df, how='left', left_on=['categoria', 'Diferencia'], right_on=['categoria', 'rango_dif'])

fig = px.bar(
    conteo_reset,
    x='categoria',
    y='Cantidad',
    color='Diferencia',
    category_orders={'Diferencia': labels},
    title='Distribución de partidos por diferencia de puntos',
    text_auto=True,
    custom_data=['info_partido']
)
fig.update_traces(
    hovertemplate='<b>%{x}</b><br> Cantidad: %{y}<br>Partidos:<br>%{customdata[0]}'
)
st.plotly_chart(fig, use_container_width=True)

# --- Tabla única con selector de cantidad/porcentaje y fila total global
partidos_all = partidos.copy()
partidos_all['diferencia'] = (partidos_all['ptsL'] - partidos_all['ptsV']).abs()
partidos_all['rango_dif'] = pd.cut(partidos_all['diferencia'], bins=bins, labels=labels, right=False)

conteo_zonas = partidos_all.groupby(['zona', 'rango_dif']).size().unstack(fill_value=0)
conteo_zonas = conteo_zonas[labels]  # asegurar orden de columnas

# Selector para mostrar cantidad o porcentaje
tipo_tabla = st.radio("Mostrar:", ["Cantidad", "%"], horizontal=True, key="tipo_tabla_zonas")

if tipo_tabla == "%":
    tabla = conteo_zonas.div(conteo_zonas.sum(axis=1), axis=0).multiply(100).round(1)
    tabla_label = "Porcentaje de partidos por diferencia (%)"
else:
    tabla = conteo_zonas.copy()
    tabla_label = "Cantidad de partidos por diferencia"

# Fila total global (suma o porcentaje global)
if tipo_tabla == "%":
    total = partidos_all['rango_dif'].value_counts().reindex(labels, fill_value=0)
    total_pct = (total / total.sum() * 100).round(1)
    total_row = pd.DataFrame([total_pct], index=["% Total"])
else:
    total = partidos_all['rango_dif'].value_counts().reindex(labels, fill_value=0)
    total_row = pd.DataFrame([total], index=["Total"])

# Concatenar fila total
tabla_final = pd.concat([tabla, total_row], axis=0)
st.dataframe(tabla_final, use_container_width=True)

# Preparar datos para gráfico apilado
conteo_zonas_reset = conteo_zonas.reset_index().melt(id_vars='zona', var_name='Diferencia', value_name='Cantidad')

fig_zonas = px.bar(
    conteo_zonas_reset,
    x='zona',
    y='Cantidad',
    color='Diferencia',
    category_orders={'Diferencia': labels, 'zona': sorted(conteo_zonas.index)},
    title='Comparativa de zonas: partidos por diferencia de puntos',
    text_auto=True
)
fig_zonas.update_traces(
    hovertemplate='<b>%{x}</b><br>Diferencia: %{customdata[0]}<br>Cantidad: %{y}',
    customdata=conteo_zonas_reset[['Diferencia']].values
)
st.plotly_chart(fig_zonas, use_container_width=True)