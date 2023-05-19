import csv
import json
import numpy as np


tiempo_anterior=0
Tiempo_Vuelta=0
Tiempo_paso	= 0
metasList=[]
Tiempo=0
json_object=""
rolling=0
LDRDRow=17
LDRIRow=21
Diferencia_paso = 0
MetaThreshold = 70  

clockwise=1

with open('contadorvueltas1.csv')as file:
 reader=csv.reader(file)
 row1=next(reader)
 tiempo_inicio=float(row1[3])
 print("Tiempoinicio",tiempo_inicio/1000000)


 with open("metas.json","r")as rf:
     meta_data=json.load(rf)

     contadorvueltas=0
     
     LDR=0
     Tiempo=0
     valor_anterior=float(row1[1])
     count=0

     for row in reader:
         LDR=float(row[1])
         Tiempo=float(row[3])


         if LDR-valor_anterior>MetaThreshold:
             if Tiempo-tiempo_anterior>100000:
                 print("Cambio:",Tiempo/1000000,LDR-valor_anterior)
                 Tiempo_Vuelta=meta_data[contadorvueltas]['Tiempo Vuelta (s)']
                 Tiempo_paso = meta_data[contadorvueltas]['Tiempo paso por meta (s)']


                 meta={"Vuelta Nº":contadorvueltas,"Tiempo Vuelta(s)":(Tiempo/1000000-tiempo_anterior/1000000),"Tiempo Vuelta coche(s)":Tiempo_Vuelta,"Diferencia":abs(Tiempo_Vuelta-(Tiempo/1000000-tiempo_anterior/1000000)),
                 "Tiempo paso por meta(s)":Tiempo/1000000, "Tiempo paso por meta(s) coche":Tiempo_paso,"Diferencia paso":abs(Tiempo/1000000 - Tiempo_paso),"Diferencia con paso anterior":abs( abs(Tiempo/1000000 - Tiempo_paso) - Diferencia_paso),
                 "Tiempo desde primer mensaje (s)":Tiempo/1000000-tiempo_inicio/1000000,
                 "LDR":LDR,}
                 Diferencia_paso = abs(Tiempo/1000000 - Tiempo_paso)

                 if (contadorvueltas != len(meta_data)-1 ):
                     contadorvueltas+=1
                 tiempo_anterior=Tiempo;
                 
                 metasList.append(meta)
                 json_object=json.dumps(metasList,indent=5)

         valor_anterior=LDR
         

with open("resultadoscontador.json","w")as outfile:
 outfile.write(json_object+"\n")
