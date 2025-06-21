import pandas as pd
import openpyxl

#anio;categoria;fase;ronda;nivel;zona;grupo;jornada;fecha;local;ptsL;visitante;ptsV

#Lee el archivo
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

def asignar_puntos(teams,Equipo,puntos):
    i=0
    for fila in teams:
        i+=1
        if fila[0]==Equipo:
            teams[i-1][1]+=puntos
            i+=1
            break

def Game_Value(File,teams):
    #by result
    for index, row in File.iterrows():
        LocalPoints=-50
        visitPoint=50

        if row["categoria"]=="PREMINI" or row["categoria"]=="MINI":
        #partido no jugado gana local
            if (row["ptsL"]==20 and row["ptsV"]==0):
                LocalPoints=LocalPoints+700
                continue
        #Partido no jugado gana visita
            elif (row["ptsL"]==0 and row["ptsV"]==20):
                visitPoint=visitPoint+700
                continue
            else:
                continue

        else:   
            #Ya se que la categoria es la que tengo que contar

            #partido no jugado gana local
            if (row["ptsL"]==20 and row["ptsV"]==0):
                LocalPoints=LocalPoints+700

            #Partido no jugado gana visita
            elif (row["ptsL"]==0 and row["ptsV"]==20):
                visitPoint=visitPoint+700

            #gana local 
            elif row["ptsL"]>row["ptsV"]:
                #Bonus por localia
                if row["fase"]=="FINAL FOUR":
                    #pones en 0 for ser neutral
                    LocalPoints=LocalPoints+50
                    visitPoint=visitPoint-50

                #gana por 9 o menos 
                if (row["ptsL"]-row["ptsV"])<=9:
                    LocalPoints=LocalPoints+650
                    visitPoint=visitPoint+350
                #gana por mas de 10 o menos 20
                elif (row["ptsL"]-row["ptsV"])>=10 and (row["ptsL"]-row["ptsV"])<20:
                    LocalPoints=LocalPoints+700
                    visitPoint=visitPoint+300
                #gana por mas de 10 o menos 20
                else:
                    LocalPoints=LocalPoints+750
                    asignar_puntos(teams,row["visitante"],250)

            #gana visita
            elif row["ptsV"]>row["ptsL"]:
                #Bonus por localia
                if row["fase"]=="FINAL FOUR":
                    #pones en 0 for ser neutral
                    LocalPoints=LocalPoints+50
                    visitPoint=visitPoint-50

                #gana por 9 o menos 
                if (row["ptsV"]-row["ptsL"])<=9:
                    visitPoint=visitPoint+650
                    LocalPoints=LocalPoints+350
                #gana por mas de 10 o menos 20
                elif (row["ptsV"]-row["ptsL"])>=10 and (row["ptsL"]-row["ptsV"])<20:
                    visitPoint=visitPoint+700
                    LocalPoints=LocalPoints+300
                #gana por mas de 10 o menos 20
                else:
                    visitPoint=visitPoint+750
                    LocalPoints=LocalPoints+250

            if row["anio"]!="2019":
                continue
            else:
                 avg=len(teams)
                 #Para local
                 i=0
                 for fila in teams:
                    i+=1
                    if fila[0]==row["local"]:
                        points=(avg)-i-1
                        i+=1
                        LocalPoints=LocalPoints+points
                        break
                    
                 #para visitante
                 for fila in teams:
                    i+=1
                    if fila[0]==row["visitante"]:
                        points=(avg)-i-1
                        i+=1
                        visitPoint=visitPoint+points
                        break
                    
            #MULTIPLICADOR POR FASE
            if row["visitante"]=="FINAL FOUR":
                m=1.25
            elif row["fase"]=="Playoff":
                m=0.75
            else:
                m=0.5

            asignar_puntos(teams,row["local"],LocalPoints*m)
            asignar_puntos(teams,row["visitante"],visitPoint*m)   

data=Read_csv("19-24")
Allequipos=read_teams(data)
Game_Value(data,Allequipos)

print(Allequipos)
resultados_ordenados = sorted(Allequipos, key=lambda item: item[1], reverse=True)
print(resultados_ordenados)

nombres_columnas = ['Equipo', 'Puntos']
df_resultados2=pd.DataFrame(Allequipos, columns=nombres_columnas)
df_resultados=pd.DataFrame(resultados_ordenados, columns=nombres_columnas)
df_resultados.to_excel("archivo_excel_salida.xlsx", index=False, engine='openpyxl', sheet_name='Resultados')
df_resultados2.to_excel("archivo_excel_salida2.xlsx", index=False, engine='openpyxl', sheet_name='Resultados')