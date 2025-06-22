import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pandas as pd
from utils.open_csv import leer_csv_con_encoding_detectado , leer_csv_con_encoding_detectado_Comas

#Lee y devuelve una lista de equipos.
def crear_ranking_base(data):
    # Normaliza los nombres de los equipos
    data["local"] = data["local"].str.strip().str.upper()
    data["visitante"] = data["visitante"].str.strip().str.upper()
    # Eliminar filas con valores nulos en las columnas 'local' y 'visitante' o NaN
    data = data.dropna(subset=["local", "visitante"])
    # Eliminar filas donde los equipos dice Libre
    data = data[~data["local"].str.contains("LIBRE", case=False, na=False)]

    return pd.DataFrame({"Equipo": data["local"].unique(), "Puntos": 0})

def asignar_basis_points(row):
    try:
        ptsL = int(row["ptsL"])
        ptsV = int(row["ptsV"])
    
        # Casos especiales
        if ptsL == 20 and ptsV == 0:
#            print(f"[LOG] Partido: {row['local']} {ptsL}-{ptsV} {row['visitante']} | BP: 700-0")
            return (700, 0)
        if ptsL == 0 and ptsV == 20:
#            print(f"[LOG] Partido: {row['local']} {ptsL}-{ptsV} {row['visitante']} | BP: 0-700")
            return (0, 700)
        if ptsL == 0 and ptsV == 0:
#            print(f"[LOG] Partido: {row['local']} {ptsL}-{ptsV} {row['visitante']} | BP: 0-0")
            return (0, 0)

        diff = abs(ptsL - ptsV)
        if ptsL > ptsV:
            if diff >= 20:
#                print(f"[LOG] Partido: {row['local']} {ptsL}-{ptsV} {row['visitante']} | BP: 750-250")
                return (750, 250)
            elif diff >= 10:
#                print(f"[LOG] Partido: {row['local']} {ptsL}-{ptsV} {row['visitante']} | BP: 700-300")
                return (700, 300)
            else:
#               print(f"[LOG] Partido: {row['local']} {ptsL}-{ptsV} {row['visitante']} | BP: 650-350")
                return (650, 350)
        elif ptsV > ptsL:
            if diff >= 20:
#                print(f"[LOG] Partido: {row['local']} {ptsL}-{ptsV} {row['visitante']} | BP: 250-750")
                return (250, 750)
            elif diff >= 10:
#                print(f"[LOG] Partido: {row['local']} {ptsL}-{ptsV} {row['visitante']} | BP: 300-700")
                return (300, 700)
            else:
#                print(f"[LOG] Partido: {row['local']} {ptsL}-{ptsV} {row['visitante']} | BP: 350-650")
                return (350, 650)
        else:
#            print(f"[LOG] Partido: {row['local']} {ptsL}-{ptsV} {row['visitante']} | BP: 0-0")
            return (0, 0)
    except ValueError:
        print(f"[LOG] Error al procesar el partido: {row}")
        return (0, 0)

def peso_por_anio(anio):
    pesos = {2019: 0.25, 2022: 0.5, 2023: 0.75, 2024: 1}
    return pesos.get(int(anio), 1)

def peso_por_fase(fase, nivel):
    fase = str(fase).upper()
    if "FINAL FOUR" in fase:
        return 1
    elif "PLAYOFF" in fase:
        if nivel in ["INTERCONFERENCIA", "INTERCONFERENCIA A", "INTERCONFERENCIA B"]:
            return 1
        else:
            return 0.75
    elif "FASE REGULAR" in fase:
        return 0.65
    return 1

def peso_por_ronda(ronda, anio):
    ronda = str(ronda).upper()
    if ronda in ["1RA FASE"]:
        return 1
    if ronda in ["2DA FASE"]:
        if anio in [2019,2022,2023]:
            return 2
        else:
            return 1
    if ronda in ["3RA FASE"]:
        if anio in [2019,2022,2023]:
            return 1
        else:
            return 2
    if ronda == "OCTAVOS DE FINAL":
        return 3
    if ronda == "CUARTOS DE FINAL":
        return 4
    if ronda == "SEMIFINAL":
        return 6
    if ronda == "FINAL":
        return 6
    return 1

def peso_por_nivel(nivel):
    nivel = str(nivel).upper()
    if "INTERCONFERENCIA A" in nivel or nivel == "INTERCONFERENCIA":
        return 2
    if "INTERCONFERENCIA B" in nivel:
        return 1.5
    if nivel == "1":
        return 1.25
    if nivel == "2":
        return 1
    if nivel == "3":
        return 1
    return 1

def Calculo_ORP(Ranking,local,visitante):
    avg=0
    for i in range(len(Ranking)):
        sum=sum+i
    avg=sum/(len(Ranking))
    
def Calculo_ORP(Ranking,local,visitante):
    sum=0
    i=1
    for i in range(len(Ranking)):
        sum=sum+i
    avg=sum/(len(Ranking))

    for i,row in Ranking.iterrows():
        if local==row["Equipo"]:
            LocalPos=i+1
        else:
            LocalPos=avg
        if visitante==row["Equipo"]:
            VisPos=i+1
        else:
            VisPos=avg
        
    
    ORPloc=1.5*(avg-VisPos)
    ORPvis=1.5*(avg-LocalPos)

    return (ORPloc , ORPvis)

data=leer_csv_con_encoding_detectado("Data/procesada/19-24.csv")    

#for year in sorted(data["anio"].unique()):
#    data_year = data[data["anio"] == year].copy()
#    for idx, row in data_year.iterrows():
#        BP_LOCAL, BP_VISITA = asignar_basis_points(row)
#        data_year.at[idx, "BP_LOCAL"] = BP_LOCAL
#        data_year.at[idx, "BP_VISITA"] = BP_VISITA
#    data_year.to_csv(f"Data/procesada/{str(year)}.csv", index=False)


#2019
# Filtrar las categorías MINI y PREMINI
#data = data[~data["categoria"].str.upper().isin(["MINI", "PREMINI"])]
#
#data_2019 = data[data["anio"] == 2019].copy()
#for idx, row in data_2019.iterrows():
#    BP_LOCAL, BP_VISITA = asignar_basis_points(row)
#    data_2019.at[idx, "BP_LOCAL"] = BP_LOCAL
#    data_2019.at[idx, "BP_VISITA"] = BP_VISITA
#    data_2019["peso_nivel"] = data_2019["nivel"].apply(peso_por_nivel)
#    data_2019["peso_anio"] = data_2019["anio"].apply(peso_por_anio)
#    data_2019["peso_ronda"] = data_2019.apply(lambda row: peso_por_ronda(row["ronda"], row["anio"]), axis=1)
#    #data_2019["peso_fase"] = data_2019.apply(lambda row: peso_por_fase(row["fase"], row["nivel"]), axis=1)
#    data_2019["peso_fase"] = (peso_por_fase(data_2019["fase"],data_2019["nivel"]))
#    data_2019["LocalSuma"] = data_2019["peso_fase"]*data_2019["peso_ronda"]*data_2019["peso_anio"]*data_2019["peso_nivel"]*data_2019["BP_LOCAL"]
#    data_2019["VisitaSuma"] = data_2019["peso_fase"]*data_2019["peso_ronda"]*data_2019["peso_anio"]*data_2019["peso_nivel"]*data_2019["BP_VISITA"]
#
#
#data_2019 = data_2019[["local", "visitante", "BP_LOCAL", "BP_VISITA", "peso_anio", "peso_nivel", "peso_fase", "peso_ronda","LocalSuma","VisitaSuma"]].copy()
#data_2019.to_csv("Data/procesada/2019.csv", index=False)
#data_2019_local = data_2019.groupby("local").agg({"LocalSuma": "sum"}).reset_index()
#data_2019_visitante = data_2019.groupby("visitante").agg({"VisitaSuma": "sum"}).reset_index()
#data_2019_local.columns = ["Equipo", "Puntos"]
#data_2019_visitante.columns = ["Equipo", "Puntos"]
#ranking_2019 = pd.concat([data_2019_local, data_2019_visitante]).groupby("Equipo", as_index=False).agg({"Puntos": "sum"})
#ranking_2019 = ranking_2019.sort_values(by="Puntos", ascending=False).reset_index(drop=True)
#
#print(ranking_2019)
#ranking_2019.to_csv("Data/procesada/Ranking2019.csv", index=False)



#2022
ano=2022
data = data[~data["categoria"].str.upper().isin(["MINI", "PREMINI"])]
#import ranking previo
PrevRanking=leer_csv_con_encoding_detectado_Comas("Data/procesada/Ranking2019.csv")

data_2022 = data[data["anio"] == 2022].copy()
for idx, row in data_2022.iterrows():
    BP_LOCAL, BP_VISITA = asignar_basis_points(row)
    data_2022.at[idx, "BP_LOCAL"] = BP_LOCAL
    data_2022.at[idx, "BP_VISITA"] = BP_VISITA
    ORP_LOCAL , ORP_VIST=Calculo_ORP(PrevRanking,row["local"],row["visitante"])
    data_2022.at[idx, "ORP_LOCAL"] = ORP_LOCAL
    data_2022.at[idx, "ORP_VISITA"] = ORP_VIST
    data_2022["peso_nivel"] = data_2022["nivel"].apply(peso_por_nivel)
    data_2022["peso_anio"] = data_2022["anio"].apply(peso_por_anio)
    data_2022["peso_ronda"] = data_2022.apply(lambda row: peso_por_ronda(row["ronda"], row["anio"]), axis=1)
    #data_2019["peso_fase"] = data_2019.apply(lambda row: peso_por_fase(row["fase"], row["nivel"]), axis=1)

    data_2022["peso_fase"] = (peso_por_fase(data_2022["fase"],data_2022["nivel"]))
    data_2022["LocalSuma"] = data_2022["peso_fase"]*data_2022["peso_ronda"]*data_2022["peso_anio"]*data_2022["peso_nivel"]*(data_2022["BP_LOCAL"]+data_2022["ORP_LOCAL"])
    data_2022["VisitaSuma"] = data_2022["peso_fase"]*data_2022["peso_ronda"]*data_2022["peso_anio"]*data_2022["peso_nivel"]*(data_2022["BP_VISITA"]+data_2022["ORP_VISITA"])


data_2022 = data_2022[["local", "visitante", "BP_LOCAL", "BP_VISITA","ORP_LOCAL", "ORP_VISITA", "peso_anio", "peso_nivel", "peso_fase", "peso_ronda","LocalSuma","VisitaSuma"]].copy()
data_2022.to_csv("Data/procesada/2022.csv", index=False)
data_2022_local = data_2022.groupby("local").agg({"LocalSuma": "sum"}).reset_index()
data_2022_visitante = data_2022.groupby("visitante").agg({"VisitaSuma": "sum"}).reset_index()
data_2022_local.columns = ["Equipo", "Puntos"]
data_2022_visitante.columns = ["Equipo", "Puntos"]
ranking_2022 = pd.concat([data_2022_local, data_2022_visitante]).groupby("Equipo", as_index=False).agg({"Puntos": "sum"})
ranking_2022 = ranking_2022.sort_values(by="Puntos", ascending=False).reset_index(drop=True)

print(ranking_2022)
ranking_2022.to_csv("Data/procesada/Ranking2022.csv", index=False)