import os
import pandas as pd
from utils.open_csv import leer_csv_con_encoding_detectado
from mapeos.loader import normalizar_equipo, cargar_mapeo_equipos
# Cargar el mapeo de equipos

mapeo_equipos = cargar_mapeo_equipos()

# Ruta a la carpeta con los CSVs
carpeta_data = 'Data'
carpeta_salida = os.path.join(carpeta_data, 'procesada')
os.makedirs(carpeta_salida, exist_ok=True)

# Lista para almacenar los DataFrames corregidos
dataframes = []

# Recorremos todos los CSV de la carpeta Data
for archivo in os.listdir(carpeta_data):
    ruta_archivo = os.path.join(carpeta_data, archivo)

    if archivo.endswith('.csv') and os.path.isfile(ruta_archivo):
        print(f'Procesando: {archivo}')
        df = leer_csv_con_encoding_detectado(ruta_archivo)

        # Normalizamos los nombres de los equipos
        df['local'] = df['local'].apply(lambda x: normalizar_equipo(x, mapeo_equipos))
        df['visitante'] = df['visitante'].apply(lambda x: normalizar_equipo(x, mapeo_equipos))

        dataframes.append(df)

# Concatenamos todo en un único DataFrame
df_final = pd.concat(dataframes, ignore_index=True)

# Guardamos el resultado
ruta_salida = os.path.join(carpeta_salida, '19-24 procesado.csv')
df_final.to_csv(ruta_salida, sep=';', index=False)

print(f'Archivo guardado en: {ruta_salida}')
