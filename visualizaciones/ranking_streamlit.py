import streamlit as st
import pandas as pd
import plotly.express as px

# Diccionario de archivos por temporada
archivos = {
    "2019": "Data/procesada/Ranking2019-2019.csv",
    "2022": "Data/procesada/Ranking2019-2022.csv",
    "2023": "Data/procesada/Ranking2019-2023.csv",
    "2024": "Data/procesada/Ranking2019-2024.csv",
}

# Selector de temporada
temporada = st.selectbox("Selecciona la temporada", list(archivos.keys()))

# Cargar el archivo correspondiente
df = pd.read_csv(archivos[temporada])

# Redondear los puntos a 0 decimales
df["Puntos"] = df["Puntos"].round(0)

# Mostrar la tabla
st.title(f"Ranking Temporada {temporada}")
st.dataframe(df)

# Lineplot de posiciones de los primeros 30 equipos a lo largo de las temporadas
st.subheader("Evolución de posiciones comparativa de los equipos")

# Cargar todos los rankings en un solo DataFrame
ranking_dfs = {}
for temp, path in archivos.items():
    temp_df = pd.read_csv(path)
    temp_df["Puntos"] = temp_df["Puntos"].round(0)
    temp_df["Temporada"] = temp
    temp_df["Posición"] = range(1, len(temp_df) + 1)
    ranking_dfs[temp] = temp_df

df_all = pd.concat(ranking_dfs.values(), ignore_index=True)

# Determinar la cantidad máxima de colores distinguibles en plotly (aprox 10-12 para líneas)
max_equipos = 12

# Encontrar los equipos con mejor posición promedio (top N)
equipos_topN = (
    df_all.groupby("Equipo")["Posición"].mean().nsmallest(max_equipos).index.tolist()
)
df_topN_all = df_all[df_all["Equipo"].isin(equipos_topN)]

# Crear gráfico interactivo con tooltip usando plotly
orden_temporadas = ["2019", "2022", "2023", "2024"]
df_topN_all["Temporada_num"] = df_topN_all["Temporada"].map({"2019": 2019, "2022": 2022, "2023": 2023, "2024": 2024})

# Permitir al usuario elegir hasta 10 equipos para comparar
primeros_10 = df_all.groupby("Equipo")["Posición"].mean().nsmallest(10).index.tolist()
equipos_unicos = df_all["Equipo"].unique().tolist()
equipos_seleccionados = st.multiselect(
    "Selecciona hasta 10 equipos para comparar:",
    options=equipos_unicos,
    default=primeros_10,
    max_selections=10
)

# Filtrar el DataFrame según los equipos seleccionados
df_seleccion = df_all[df_all["Equipo"].isin(equipos_seleccionados)]
df_seleccion["Temporada_num"] = df_seleccion["Temporada"].map({"2019": 2019, "2022": 2022, "2023": 2023, "2024": 2024})

fig = px.line(
    df_seleccion,
    x="Temporada_num",
    y="Posición",
    color="Equipo",
    markers=True,
    hover_data={"Equipo": True, "Puntos": True, "Posición": True, "Temporada": True},
    title="Evolución de posiciones de equipos seleccionados por temporada (1 = más alto)"
)
fig.update_yaxes(autorange="reversed", title="Posición")
fig.update_xaxes(
    title="Temporada",
    tickvals=[2019, 2022, 2023, 2024],
    ticktext=["2019", "2022", "2023", "2024"],
    dtick=1
)
fig.update_layout(legend_title_text='Equipo', legend=dict(font=dict(size=10)))
st.plotly_chart(fig, use_container_width=True)
