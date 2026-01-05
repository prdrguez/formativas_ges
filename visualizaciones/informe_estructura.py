import plotly.express as px
import pandas as pd

df = pd.read_csv("outputs/resumen_estructura_por_anio.csv")

# Crear columna anio_nivel
df["anio_nivel"] = df["anio"].astype(str) + " - Nivel " + df["nivel"].astype(str)

# Tooltip enriquecido
df["tooltip"] = (
    "Año: " + df["anio"].astype(str) +
    "<br>Ronda: " + df["ronda"] +
    "<br>Nivel: " + df["nivel"].astype(str) +
    "<br>Zona: " + df["zona"] +
    "<br>Grupo: " + df["grupo"] +
    "<br>Equipos:<br>" + df["equipos"].str.replace(", ", "<br>")
)

# Crear gráfico
fig = px.bar(
    df,
    x="anio_nivel",
    y="cantidad_tiras",
    color="zona",
    facet_row="ronda",
    text="cantidad_tiras",
    hover_data={"tooltip": True},
    title="Estructura del Torneo por Año y Nivel",
)

# Personalización del layout
fig.update_traces(hovertemplate="%{customdata[0]}")
fig.update_layout(
    height=1200,
    barmode="group",
    xaxis_title="Año - Nivel",
    yaxis_title="Cantidad de Tiras",
    margin=dict(t=60, b=100),
    hoverlabel=dict(bgcolor="white", font_size=12),
)

fig.show()