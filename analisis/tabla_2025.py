import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from utils.open_csv import leer_csv_con_encoding_detectado
from pathlib import Path

# Leer el archivo CSV de partidos
partidos = leer_csv_con_encoding_detectado('Data/partidos_2025.csv', ";")

# Normalizar nombres de categorías para facilitar el filtrado
def normalizar_categoria(cat):
    return cat.strip().upper()

partidos['categoria'] = partidos['categoria'].apply(normalizar_categoria)

# Definir categorías especiales
CATS_PRESENTACION = {'MINI', 'PREMINI'}
CATS_2PTS = {'PREINFANTILES', 'INFANTILES', 'CADETES'}
CATS_1PT_PRESENTACION = {'MINI', 'PREMINI'}
ALL_CATS = CATS_2PTS | CATS_1PT_PRESENTACION

# --- FUNCIONES DE PUNTOS SEGÚN TIPO DE TABLA ---
def calcular_puntos_categoria(row):
    # Todas las categorías: 2 pts ganado, 1 perdido, 0 si no presentado (20-0 o 0-20)
    if row['ptsL'] == 20 and row['ptsV'] == 0:
        return pd.Series({row['local']: 2, row['visitante']: 0})
    if row['ptsL'] == 0 and row['ptsV'] == 20:
        return pd.Series({row['local']: 0, row['visitante']: 2})
    if row['ptsL'] > row['ptsV']:
        return pd.Series({row['local']: 2, row['visitante']: 1})
    elif row['ptsL'] < row['ptsV']:
        return pd.Series({row['local']: 1, row['visitante']: 2})
    elif row['ptsL'] == 0 and row['ptsV'] == 0:
        return pd.Series({row['local']: 0, row['visitante']: 0})
    else:
        return pd.Series({row['local']: 1, row['visitante']: 1})

def calcular_puntos_general(row):
    # PREINFANTILES, INFANTILES, CADETES: 2 pts ganado, 1 perdido, 0 si no presentado (20-0 o 0-20)
    if row['categoria'] in CATS_2PTS:
        if row['ptsL'] == 20 and row['ptsV'] == 0:
            return pd.Series({row['local']: 2, row['visitante']: 0})
        if row['ptsL'] == 0 and row['ptsV'] == 20:
            return pd.Series({row['local']: 0, row['visitante']: 2})
        if row['ptsL'] > row['ptsV']:
            return pd.Series({row['local']: 2, row['visitante']: 1})
        elif row['ptsL'] < row['ptsV']:
            return pd.Series({row['local']: 1, row['visitante']: 2})
        elif row['ptsL'] == 0 and row['ptsV'] == 0:
            return pd.Series({row['local']: 0, row['visitante']: 0})
        else:
            return pd.Series({row['local']: 1, row['visitante']: 1})
    # MINI, PREMINI: 1 punto por presentación, 20-0 solo suma el que hizo 20, 0-0 ninguno
    elif row['categoria'] in CATS_1PT_PRESENTACION:
        if row['ptsL'] == 20 and row['ptsV'] == 0:
            return pd.Series({row['local']: 1, row['visitante']: 0})
        if row['ptsL'] == 0 and row['ptsV'] == 20:
            return pd.Series({row['local']: 0, row['visitante']: 1})
        if row['ptsL'] == 0 and row['ptsV'] == 0:
            return pd.Series({row['local']: 0, row['visitante']: 0})
        # Ambos se presentaron
        return pd.Series({row['local']: 1, row['visitante']: 1})
    else:
        return pd.Series({row['local']: 0, row['visitante']: 0})

def calcular_estadisticas(df):
    equipos = {}
    for idx, row in df.iterrows():
        for local_visit, rival_visit, pts_equipo, pts_rival in [
            ('local', 'visitante', 'ptsL', 'ptsV'),
            ('visitante', 'local', 'ptsV', 'ptsL')
        ]:
            equipo = row[local_visit]
            rival = row[rival_visit]
            if equipo not in equipos:
                equipos[equipo] = {'EQUIPO': equipo, 'PJ': 0, 'PG': 0, 'PP': 0, 'NP': 0, 'PF': 0, 'PC': 0}
            equipos[equipo]['PJ'] += 1
            equipos[equipo]['PF'] += row[pts_equipo]
            equipos[equipo]['PC'] += row[pts_rival]
            # No presentado
            if (row[pts_equipo] == 0 and row[pts_rival] == 20):
                equipos[equipo]['NP'] += 1
            # Ganado
            elif row[pts_equipo] > row[pts_rival]:
                equipos[equipo]['PG'] += 1
            # Perdido
            elif row[pts_equipo] < row[pts_rival]:
                equipos[equipo]['PP'] += 1
    df_est = pd.DataFrame(list(equipos.values()))
    df_est['DP'] = df_est['PF'] - df_est['PC']
    return df_est.set_index('EQUIPO')

# --- TABLAS POR CATEGORIA, ZONA-GRUPO ---
tablas_cat_zonagrupo = {}
for cat in partidos['categoria'].unique():
    df_cat = partidos[partidos['categoria'] == cat]
    puntos_cat = df_cat.apply(calcular_puntos_categoria, axis=1).fillna(0)
    df_cat = pd.concat([df_cat, puntos_cat], axis=1)
    for (zona, grupo), df_zg in df_cat.groupby(['zona', 'grupo']):
        tabla = calcular_estadisticas(df_zg)
        tabla['puntos'] = 0
        for idx, row in df_zg.iterrows():
            for equipo in [row['local'], row['visitante']]:
                tabla.at[equipo, 'puntos'] += row.get(equipo, 0)
        tabla = tabla.sort_values(['puntos', 'DP', 'PF'], ascending=[False, False, False])
        tablas_cat_zonagrupo[(cat, zona, grupo)] = tabla

# --- TABLAS POR CATEGORIA, ZONA ---
tablas_cat_zona = {}
for cat in partidos['categoria'].unique():
    df_cat = partidos[partidos['categoria'] == cat]
    puntos_cat = df_cat.apply(calcular_puntos_categoria, axis=1).fillna(0)
    df_cat = pd.concat([df_cat, puntos_cat], axis=1)
    for zona, df_z in df_cat.groupby('zona'):
        tabla = calcular_estadisticas(df_z)
        tabla['puntos'] = 0
        for idx, row in df_z.iterrows():
            for equipo in [row['local'], row['visitante']]:
                tabla.at[equipo, 'puntos'] += row.get(equipo, 0)
        tabla = tabla.sort_values(['puntos', 'DP', 'PF'], ascending=[False, False, False])
        tablas_cat_zona[(cat, zona)] = tabla

# --- TABLA GENERAL POR ZONA (todas las categorías, SOLO para tabla general) ---
tabla_general_zona = {}
# Excluir JUVENILES y aplicar lógica especial para MINI y PREMINI
partidos_general = partidos[~partidos['categoria'].str.upper().eq('JUVENILES')].copy()

def calcular_puntos_general_v2(row):
    cat = row['categoria'].upper()
    if cat in CATS_2PTS:
        if row['ptsL'] == 20 and row['ptsV'] == 0:
            return pd.Series({row['local']: 2, row['visitante']: 0})
        if row['ptsL'] == 0 and row['ptsV'] == 20:
            return pd.Series({row['local']: 0, row['visitante']: 2})
        if row['ptsL'] > row['ptsV']:
            return pd.Series({row['local']: 2, row['visitante']: 1})
        elif row['ptsL'] < row['ptsV']:
            return pd.Series({row['local']: 1, row['visitante']: 2})
        elif row['ptsL'] == 0 and row['ptsV'] == 0:
            return pd.Series({row['local']: 0, row['visitante']: 0})
        else:
            return pd.Series({row['local']: 1, row['visitante']: 1})
    elif cat in CATS_1PT_PRESENTACION:
        # 1 punto solo si se presenta (tiene puntos > 0), 0 si no se presenta (0-20 o 0-0)
        if row['ptsL'] == 20 and row['ptsV'] == 0:
            return pd.Series({row['local']: 1, row['visitante']: 0})
        if row['ptsL'] == 0 and row['ptsV'] == 20:
            return pd.Series({row['local']: 0, row['visitante']: 1})
        if row['ptsL'] == 0 and row['ptsV'] == 0:
            return pd.Series({row['local']: 0, row['visitante']: 0})
        # Ambos se presentaron
        return pd.Series({row['local']: 1, row['visitante']: 1})
    else:
        return pd.Series({row['local']: 0, row['visitante']: 0})

puntos_general = partidos_general.apply(calcular_puntos_general_v2, axis=1).fillna(0)
partidos_general = pd.concat([partidos_general, puntos_general], axis=1)

def calcular_estadisticas_general(df):
    equipos = {}
    for idx, row in df.iterrows():
        for local_visit, rival_visit, pts_equipo, pts_rival in [
            ('local', 'visitante', 'ptsL', 'ptsV'),
            ('visitante', 'local', 'ptsV', 'ptsL')
        ]:
            equipo = row[local_visit]
            cat = row['categoria'].upper()
            if equipo not in equipos:
                equipos[equipo] = {'EQUIPO': equipo, 'PJ': 0, 'PG': 0, 'PP': 0, 'NP': 0, 'PF': 0, 'PC': 0, 'puntos': 0}
            equipos[equipo]['PJ'] += 1
            equipos[equipo]['PF'] += row[pts_equipo]
            equipos[equipo]['PC'] += row[pts_rival]
            if cat in CATS_1PT_PRESENTACION:
                # MINI y PREMINI: solo NP si no se presenta (0-20 o 0-0)
                if (row[pts_equipo] == 0 and row[pts_rival] == 20):
                    equipos[equipo]['NP'] += 1
            else:
                # PG, PP, NP normal
                if row[pts_equipo] == 0 and row[pts_rival] == 20:
                    equipos[equipo]['NP'] += 1
                elif row[pts_equipo] > row[pts_rival]:
                    equipos[equipo]['PG'] += 1
                elif row[pts_equipo] < row[pts_rival]:
                    equipos[equipo]['PP'] += 1
            equipos[equipo]['puntos'] += row.get(equipo, 0)
    df_est = pd.DataFrame(list(equipos.values()))
    df_est['DP'] = df_est['PF'] - df_est['PC']
    df_est = df_est.sort_values(['puntos', 'DP', 'PF'], ascending=[False, False, False])
    return df_est.set_index('EQUIPO')

for zona, df_z in partidos_general.groupby('zona'):
    tabla = calcular_estadisticas_general(df_z)
    tabla_general_zona[zona] = tabla

# Guardar resultados con estructura de carpetas solicitada
for key, df in tablas_cat_zonagrupo.items():
    cat, zona, grupo = key
    dir_path = Path(f'outputs/{zona}/{grupo}/{cat}')
    dir_path.mkdir(parents=True, exist_ok=True)
    df.to_csv(dir_path / 'tabla.csv')
for key, df in tablas_cat_zona.items():
    cat, zona = key
    dir_path = Path(f'outputs/{zona}/{cat}')
    dir_path.mkdir(parents=True, exist_ok=True)
    df.to_csv(dir_path / 'tabla.csv')
for zona, df in tabla_general_zona.items():
    dir_path = Path(f'outputs/{zona}')
    dir_path.mkdir(parents=True, exist_ok=True)
    df.to_csv(dir_path / 'tabla_general.csv')

print('Tablas de posiciones generadas en la estructura de carpetas solicitada.')