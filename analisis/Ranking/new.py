

import pandas as pd

def Read_csv(file):
    df = pd.read_csv(f"{file}.csv", sep=';')
    return df

#Lee y devuelve una lista de equipos.
def read_teams(File):
    IndTeam=[]
    for index, row in File.iterrows():
       if row["local"] in IndTeam:
           continue
       else:
           IndTeam.append([row["local"],0])
    return IndTeam

data=Read_csv("19-24")
Allequipos=read_teams(data)

print(len(Allequipos))