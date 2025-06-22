import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pandas as pd
import chardet

def leer_csv_con_encoding_detectado_2(path):
    with open(path, 'rb') as file:
        result = chardet.detect(file.read())
    return pd.read_csv(path, encoding=result['encoding'], sep=",")

def Calculo_ORP(Ranking,local,visitante):
    sum=0
    i=1
    for i in range(len(Ranking)):
        sum=sum+i
    avg=sum/(len(Ranking))
    #print(len(Ranking))
    print(avg)

    #print(type(Ranking))
    for i,row in Ranking.iterrows():
        if local==row["Equipo"]:
            LocalPos=i+1
            #print(LocalPos)
        if visitante==row["Equipo"]:
            VisPos=i+1
            #print(VisPos)
    
    ORPloc=1.5*(avg-VisPos)
    ORPvis=1.5*(avg-LocalPos)

    return (ORPloc , ORPvis)

Ranking=leer_csv_con_encoding_detectado_2("Data/procesada/teams.csv")
#print(Ranking)
#print(type(Ranking))
ORP1 , ORP2 = Calculo_ORP(Ranking,"DEFENSORES DE BANFIELD","SITAS")
print(ORP1 , ORP2)
print (1.5*(102.5-23))
print (1.5*(102.5-7))