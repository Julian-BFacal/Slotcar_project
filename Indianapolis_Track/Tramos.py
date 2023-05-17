import csv 
import json
import numpy as np
import math
import time



metasList = []    
json_object = ""
json_object_meta = ""
tramosList = []
TrackMap = []

class contador_class:

    contadorvueltas = 0
    contadortramo = 0
    contadorsector = 0


class values_class:

    GyroZ = 0
    LDRD = 0
    LDRI = 0


    RectaThreshold = 50
    LDRDThreshold = -60
    LDRIThreshold =  -30
    MetaThreshold = -20
    DerrapeThreshold = 400
    TiempoThreshold = 100000
    valor_anteriorD = 0
    valor_anteriorI = 0
    tiempo_anterior = 0
    tiempo_anterior_derrape = 0
    Tiempo = 0
    tiempo_ultimameta = 0


    valor_futuroD = 0
    valor_futuroI = 0




    tiempo_rolling = 0
    rolling = 0

    exploring = 0


    LDRDRow = 17
    LDRIRow = 21

    last_value = ""
 
    result = []



class Ventana_class:

    ventanamediana = 0
    dataGyro = []
    dataLDRI = []
    dataLDRD = []
    future_Gyro = []
    future_LDRD = []
    future_LDRI = []
    clockwise = 1



def Jsonoutput(v,c,tipo):
    if tipo == "meta":
        Jsontipo = {
            "**************NUEVA VUELTA***************** NUMERO": c.contadorvueltas,
            "Tiempo Vuelta (s)": (v.Tiempo/1000000 - v.tiempo_ultimameta/1000000),
            "Tiempo paso por meta (s)": v.Tiempo/1000000,
            "Tiempo desde primer mensaje (s)": v.Tiempo/1000000 - tiempo_inicio/1000000,
            "(Vuelta / Sector) Nº": format(c.contadorvueltas + c.contadorsector/100,'.2f'),
            "(Sector / Tramo) Nº":  format(c.contadorsector + c.contadortramo/100,'.2f'),
            "Tiempo Tramo (s)": (v.Tiempo/1000000 - v.tiempo_anterior/1000000),
        }
    elif tipo == "recta": 
        Jsontipo = {
        	"_____________RECTA_____________": "",
        	"(Vuelta / Sector) Nº": format(c.contadorvueltas + c.contadorsector/100,'.2f'),
            "(Sector / Tramo) Nº":  format(c.contadorsector + c.contadortramo/100,'.2f'),
            "Tiempo Tramo (s)": (v.Tiempo/1000000 - v.tiempo_anterior/1000000),
            "Tiempo paso por tramo (s)": v.Tiempo/1000000,
            "Tiempo desde primer mensaje (s)": v.Tiempo/1000000 - tiempo_inicio/1000000,
        }
    elif tipo == "curva":
        Jsontipo = {
            ".............CURVA.............": "",
        	"(Vuelta / Sector) Nº": format(c.contadorvueltas + c.contadorsector/100,'.2f'),
            "(Sector / Tramo) Nº":  format(c.contadorsector + c.contadortramo/100,'.2f'),
            "Tiempo Tramo (s)": (v.Tiempo/1000000 - v.tiempo_anterior/1000000),
            "Tiempo paso por tramo (s)": v.Tiempo/1000000,
            "Tiempo desde primer mensaje (s)": v.Tiempo/1000000 - tiempo_inicio/1000000,
        }
    return Jsontipo


def detectarPrimerMovimiento(values):

    if (abs(values.GyroZ) > 6) and values.rolling == 0:
        values.tiempo_rolling = values.Tiempo
        values.rolling = 1
        print("Tiempo primer movimiento", values.tiempo_rolling/1000000)



def poblarventana(row,ventana,values):

    if ventana.ventanamediana <= 3:
        if (ventana.clockwise == 0):
            values.LDRDRow = 21
            values.LDRIRow = 17
        ventana.dataGyro.append(float(row[5]))
        ventana.dataLDRD.append(float(row[values.LDRDRow]))
        ventana.dataLDRI.append(float(row[values.LDRIRow]))
        values.Tiempo = int(row[7])    
    elif ventana.ventanamediana > 3:
        ventana.future_LDRD.append(float(row[values.LDRDRow]))
        ventana.future_LDRI.append(float(row[values.LDRIRow]))
        values.Tiempo = int(row[7])    

    ventana.ventanamediana += 1

def ventanallena(ventana,values):
    if ventana.ventanamediana == 5:
        values.GyroZ = np.median(ventana.dataGyro)
        values.LDRD = np.median(ventana.dataLDRD)
        values.LDRI = np.median(ventana.dataLDRI)
        values.valor_futuroI = np.median(ventana.future_LDRI)
        values.valor_futuroD = np.median(ventana.future_LDRD)
        
        return 1
    return 0

        
def esprimeraMeta(values):

    if abs(values.GyroZ) < values.RectaThreshold:
        if values.LDRI - values.valor_anteriorI  < values.LDRIThreshold and  values.valor_futuroI - values.LDRI > 5:
            if values.LDRD - values.valor_anteriorD  < values.LDRDThreshold and  values.valor_futuroD - values.LDRD  > 5: 
                if values.exploring == 0: 
                    print("Meta",values.Tiempo/1000000)
                    return 1
    return 0

def esMeta(values):
    
    if abs(values.GyroZ) < values.RectaThreshold:
        if values.LDRI - values.valor_anteriorI  < values.MetaThreshold and values.valor_futuroI - values.LDRI  > 5:
            if values.LDRD - values.valor_anteriorD  < values.MetaThreshold and values.valor_futuroD - values.LDRD  > 5:
                if values.Tiempo - values.tiempo_ultimameta  > values.TiempoThreshold:
                    print("Meta",values.Tiempo/1000000)
                    return 1
    return 0


def esRecta(values):

    if abs(values.GyroZ) < values.RectaThreshold:
        if values.LDRI - values.valor_anteriorI  < values.LDRIThreshold and values.valor_futuroI - values.LDRI  > 50:
                if values.Tiempo - values.tiempo_anterior  > values.TiempoThreshold:
                    if ((values.Tiempo > values.tiempo_rolling) and (values.tiempo_rolling != 0)):
                        return 1
    return 0

def esCurva(values):
    if abs(values.GyroZ) < values.DerrapeThreshold:
        if values.LDRD - values.valor_anteriorD  < values.LDRDThreshold and values.valor_futuroD - values.LDRD  > 50:
            if values.Tiempo - values.tiempo_anterior  > values.TiempoThreshold:
                if ((values.Tiempo > values.tiempo_rolling) and (values.tiempo_rolling != 0)):
                    return 1
    return 0

def esDerrape(values,ventana):
    if values.Tiempo - values.tiempo_anterior_derrape > values.TiempoThreshold:
        if (ventana.clockwise == 1):
            if values.GyroZ > 100 or values.GyroZ < -450:
                return 1
        elif values.GyroZ > 450 or values.GyroZ < -100:
            return 1
    return 0


def contarVuelta(values,c):
    global tramosList
    temp_list = []

    if (values.exploring == 2):
        c.contadorsector += 1
        if (c.contadorsector <= len(values.result)):
            if (c.contadortramo != len(values.result[c.contadorsector-1])):
                meta =  {
                "Posible Perdida de": values.result[c.contadorsector-1][0],
                }
                tramosList.append(meta)
    c.contadortramo = 1
    c.contadorvueltas += 1
    c.contadorsector = 0
    contador = 0
    meta = Jsonoutput(values,contadores,"meta")
    i_antiguo = ""
    if (values.exploring == 1):
        for i in TrackMap:
 	         if i != i_antiguo and i_antiguo != ""  :
 	     	    temp_list.append(i_antiguo)
 	     	    values.result.append(temp_list)
 	     	    temp_list = []
 	         elif i_antiguo != "":
 	     	    temp_list.append(i_antiguo)
 	     	    if contador+1 == len(TrackMap):
 	     	    	temp_list.append(i)
 	     	    	values.result.append(temp_list)
 	         i_antiguo = i
 	         contador += 1

    values.exploring = 2
    values.tiempo_anterior = values.Tiempo
    values.tiempo_ultimameta = values.Tiempo
    tramosList.append(meta)
    metasList.append(meta)


def contarPrimerVuelta(values,contadores):
    global tramosList,TrackMap
    contadores.contadortramo = 1
    contadores.contadorvueltas += 1
    contadores.contadorsector = 0
    meta = Jsonoutput(values,contadores,"meta")
    
    values.tiempo_anterior = values.Tiempo
    values.tiempo_ultimameta = values.Tiempo
    tramosList.append(meta)
    metasList.append(meta)
    TrackMap.append("R")
    values.exploring = 1

def contarRecta(values,c):
    global tramosList,TrackMap

    if (values.exploring == 1):
        TrackMap.append("R")
        if (values.last_value != "C" and values.last_value  != ""):
            meta = { "Cambio a": "R"}
            tramosList.append(meta)
            c.contadorsector += 1
            c.contadortramo = 0




    elif (values.exploring == 2):
        if (values.last_value != "C" and values.last_value  != ""):
    	    c.contadorsector += 1
    	    if (c.contadorsector <= len(values.result)):
    	        if (c.contadortramo != len(values.result[c.contadorsector-1])):
                    meta =  {
                    "Posible Perdida de": values.result[c.contadorsector-1][0],
                    }
                    tramosList.append(meta)
    	    c.contadortramo = 0
    	    meta = { "Cambio a": "R"}
    	    tramosList.append(meta)

    values.last_value = "C"
    c.contadortramo += 1
    recta = Jsonoutput(values,contadores,"recta")
    values.tiempo_anterior = values.Tiempo
    tramosList.append(recta)
    
    

def contarCurva(values,c):
    global tramosList,TrackMap

    if (values.exploring == 1):
        TrackMap.append("C")
        if (values.last_value != "R" and values.last_value  != ""):
            meta = { "Cambio a": "C"}
            tramosList.append(meta)
            c.contadorsector += 1
            c.contadortramo = 0

        
 
    elif (values.exploring == 2):
        if (values.last_value != "R" and values.last_value  != ""):
    	    c.contadorsector += 1
    	    if (c.contadorsector <= len(values.result)):
    	        if (c.contadortramo != len(values.result[c.contadorsector-1])):
                    meta =  {
                    "Posible Perdida de": values.result[c.contadorsector-1][0],
                    }
                    tramosList.append(meta)

    	    c.contadortramo = 0
    	    meta = { "Cambio a": "C"}
    	    tramosList.append(meta)


    
    values.last_value = "R"
    c.contadortramo += 1

    curva = Jsonoutput(values,contadores,"curva")
    values.tiempo_anterior = values.Tiempo
    tramosList.append(curva)

with open('slotcar1.csv') as file:
    reader = csv.reader(file)
    row1 = next(reader)
    tiempo_inicio = float(row1[7])
    print("TIempo inicio",tiempo_inicio/1000000)

    ventana = Ventana_class()
    values = values_class()
    contadores = contador_class()

    for row in reader:
        
        poblarventana(row,ventana,values)

        if (ventanallena(ventana,values)):

            detectarPrimerMovimiento(values)
            
            if(esprimeraMeta(values)):

                contarPrimerVuelta(values,contadores)

            elif (esMeta(values)):

                contarVuelta(values,contadores)

            elif (esRecta(values)):
        
                contarRecta(values,contadores)
                
            elif (esCurva(values)):

                contarCurva(values,contadores)

            elif (esDerrape(values,ventana)):

                tramosList.append({"DERRAPE": values.Tiempo/1000000,})
                values.tiempo_anterior_derrape = values.Tiempo


            json_object = json.dumps(tramosList, indent=7)
            json_object_meta = json.dumps(metasList)
            ventana.dataGyro = []
            ventana.dataLDRD = []
            ventana.dataLDRI = []
            ventana.ventanamediana = 0
            values.valor_anteriorD = values.LDRD
            values.valor_anteriorI = values.LDRI

print(TrackMap) 
print(values.result)     
        

with open("resultados.json", "w") as outfile:
    outfile.write(json_object  + "\n")

with open("metas.json", "w") as outfile:
    outfile.write(json_object_meta  + "\n")




    
