# Formativas Febamba

Herramienta para seguir competencias de FEBAMBA y analizar torneos formativos. Extrae datos desde `competicionescabb.gesdeportiva.es` y los procesa para generar tablas, rankings y visualizaciones con Streamlit y Plotly.

## Objetivo del proyecto

* **Scraping y normalización** de partidos, categorías, fases y grupos de las competencias.
* **Procesamiento analítico** para construir tablas de posiciones y resúmenes de estructura.
* **Visualizaciones** para consumo en dashboards (Streamlit) y gráficos interactivos.

## Estructura del repositorio

```
Data/                      # CSVs de partidos por año y resultados procesados
analisis/                  # Scripts de análisis y generación de tablas
analisis/Ranking/          # Cálculo de ranking por temporadas
mapeos/                    # Mapas de categorías/equipos y utilidades de normalización
parsers/                   # Parsers para fases, grupos y jornadas
pipelines/                 # Pipelines de scraping y recolección de torneos
scraper/                   # Scraper principal (ETL)
utils/                     # Utilidades (logger, requester, CSV)
visualizaciones/           # Apps Streamlit y reportes Plotly
outputs/                   # Tablas y resultados generados
requirements.txt           # Dependencias de Python
```

> Nota: `outputs/` y `Data/` incluyen resultados ya generados para 2019–2025.

## Flujo general de datos

1. **Descubrimiento de torneos**: `pipelines/torneos_ges.py` recorre IDs de competencias y guarda `gesdeportiva.json` con torneos válidos.
2. **Scraping**: `scraper/main.py` define `FebambaScraper`, que navega categorías → fases → grupos → partidos.
3. **Normalización**: se corrigen nombres usando `mapeos/categorias_map.json` y `mapeos/equipos_map.json`.
4. **Postprocesamiento**: scripts en `analisis/` calculan tablas y resúmenes para `outputs/`.
5. **Visualización**: apps en `visualizaciones/` consumen los CSVs generados.

## Componentes principales

### Scraper y pipeline

* `scraper/main.py`
  * **Clase:** `FebambaScraper`
  * **Métodos clave:**
    * `scrap_torneo`: recorre todas las categorías de un torneo.
    * `_scrap_fases_categoria`: procesa fases de una categoría.
    * `_scrap_grupos_fase`: procesa grupos de una fase.
    * `_scrap_partidos_grupo`: extrae partidos por grupo.
  * Usa `utils.requester.hacer_solicitud` para reintentos y backoff.

* `pipelines/pipeline2019-2025.py`
  * Orquesta scraping por torneo (por defecto 2025).
  * Guarda CSV consolidado en `Data/` con fecha actual.

* `pipelines/torneos_ges.py`
  * Recorre el sitio de GesDeportiva y construye `gesdeportiva.json` con torneos encontrados.

### Parsers

* `parsers/fases.py`: interpreta el texto de fases (lógica específica por año).
* `parsers/grupos.py`: interpreta grupos y normaliza nivel/zona/grupo.
* `parsers/jornadas.py`: extrae ronda, jornada y fecha.
* `parsers/rondas.py`: deduce rondas para playoffs y Final Four.

### Mapeos y utilidades

* `mapeos/loader.py`: carga mapas de categorías/equipos y normaliza nombres.
* `utils/requester.py`: sesión HTTP con reintentos y backoff exponencial.
* `utils/logger.py`: logger central del proyecto.
* `utils/open_csv.py`: lectura de CSV detectando encoding (requiere `sep`).
* `utils/dataframes.py`: helpers para crear y guardar DataFrames.

### Procesos de análisis

* `corregir_nombres_postscrap.py`
  * Normaliza nombres de equipos en los CSVs de `Data/` y genera `Data/procesada/`.

* `analisis/tabla_2025.py`
  * Calcula tablas por **categoría/zona/grupo** y tabla general por zona.
  * Genera estructura de carpetas dentro de `outputs/`.

* `analisis/eda.py`
  * Filtra partidos inválidos y crea `outputs/partidos_invalidos_log.csv`.
  * Genera `outputs/resumen_estructura_por_anio.csv` con estructura por año.

* `analisis/Ranking/Functions.py`
  * Cálculo de ranking por temporadas, con ponderaciones por fase, ronda, nivel y año.
  * Guarda resultados en `Data/procesada/`.

### Visualizaciones

* `visualizaciones/ver_tabla.py`
  * App Streamlit para navegar tablas por zona/grupo/categoría.
  * Muestra resultados de partidos y tablas generales.
  * Incluye gráfico de distribución de diferencias de puntos.

* `visualizaciones/ranking_streamlit.py`
  * App Streamlit para visualizar rankings por temporada.
  * Incluye gráfico de evolución por equipo.

* `visualizaciones/informe_estructura.py`
  * Reporte Plotly con la estructura del torneo por año y nivel.

## Cómo ejecutar

### Instalación

```bash
pip install -r requirements.txt
```

### Scraping

```bash
python pipelines/pipeline2019-2025.py
```

### Normalización de nombres

```bash
python corregir_nombres_postscrap.py
```

### Generación de tablas 2025

```bash
python analisis/tabla_2025.py
```

### Informe de estructura

```bash
python analisis/eda.py
python visualizaciones/informe_estructura.py
```

### Visualizaciones (Streamlit)

```bash
streamlit run visualizaciones/ver_tabla.py
streamlit run visualizaciones/ranking_streamlit.py
```

## Datos de salida

* `Data/partidos_YYYY.csv`: partidos por temporada.
* `Data/procesada/`: CSVs consolidados y rankings.
* `outputs/`: tablas generadas por zona/grupo/categoría y resúmenes.

## Pruebas

* `tests/test_parsers.py` valida la salida de los parsers contra un CSV de referencia.

## Contribuciones

Sugerencias y colaboraciones son bienvenidas. Si agregás nuevas temporadas, ajustá los parsers y mapeos según cambios en el formato de la competencia.
