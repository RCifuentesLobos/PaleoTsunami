"""
RESTRINGE LOS MODELOS DE TSUNAMI SIN TENER EN CUENTA LOS NIVELES DE MAREA
"""
import os
import glob
import shutil 
import sys
import json
import numpy as np
import pandas as pd
from geographiclib.geodesic import Geodesic
import gc 

gc.collect()

"""
PARAMETROS DE COMPARACION
"""
# tolerancia de puntos
tol = 0
# tolerancia en metros
tol_metros = 0

"""
INFO DE DIRECTORIOS
"""
dir_fallas         = "../../fallas2/modelos_restringidos/restriccion_fuerte"
dir_modelaciones   = "../ctl_tsunami/norte_restriccion_fuerte" # ruta al directorio donde se guardan los modelos
dir_input_altura   = "../input" # directorio donde se encuentra el archivo con altura
archivo_altura     = "AlturaMaxenMetros.txt" # archivo de datos de altura
archivo_marea      = "nivel_mareas_tsunami.csv"
dir_mods_rests     = "modelos_restringidos" # directorio donde se copiara los modelos que pasen las restricciones
dir_actual         = os.getcwd()     # ruta al directorio principal 


# se crea una lista de todos los directorios dentro de dir_modelaciones que tienen datos de modelos
lista_dir_modelaciones = [f for f in os.listdir(dir_modelaciones) if os.path.isdir(os.path.join(dir_modelaciones, f))]
#lista_dir_modelaciones.sort(key=os.path.getctime) 
n_dir_modelaciones     = len(lista_dir_modelaciones) # cantidad de directorios con modelaciones


"""
LEER ARCHIVO INPUT
"""
nombre_input_file = dir_input_altura + "/" + archivo_altura
data              = np.genfromtxt(nombre_input_file,usecols=(1,2,3))
lon               = data[:,0] - 360
lat               = data[:,1]
altura            = data[:,2]


"""
LEER TS_LOCATION.DAT
"""

os.chdir(dir_modelaciones)
coords = np.genfromtxt("ts_location.dat", usecols=(0,1)) # se lee el archivo de ts_locations
lon_ts = coords[:,0] # se obtienen las longitudes
lat_ts = coords[:,1] # se obtienen las latitudes
n_ts   = len(lat_ts) # numero total de series
os.chdir(dir_actual)

"""
LEER ARCHIVO DE MAREAS
"""

input_file = dir_input_altura + "/" + archivo_marea
nombres_columnas = ["Evento","Longitud","Latitud","T o NT","Altura","Pleamar","Bajamar", "Fuente", "Localidad"]
paleo_registros  = pd.read_csv(input_file, skiprows = [0], names = nombres_columnas)
lon_medicion = np.asarray(paleo_registros.Longitud.tolist())
lat_medicion = np.asarray(paleo_registros.Latitud.tolist())
altura_ola   = np.asarray(paleo_registros.Altura.tolist())
altura_ola[altura_ola=="-"]="nan"
pleamar      = np.asarray(paleo_registros.Pleamar.tolist())
bajamar      = np.asarray(paleo_registros.Bajamar.tolist())

"""
LOOP DE RESTRICCION
"""

# lista donde se guardara los modelos que pasen las restricciones
modelos_ok = []
# se corta el archivo de datos de acuerdo a cantidad de ts
lon    = lon[0:n_ts]
lat    = lat[0:n_ts]
altura = altura[0:n_ts]
# se va al directorio de modelaciones
os.chdir(dir_modelaciones)
# loop para ir por cada una de los directorios con datos
for direc in lista_dir_modelaciones:
    os.chdir(direc)
    # lista donde se guardara los maximos de los ts_record
    max_ts = np.ones(n_ts)
    # lista donde se guardara los minimos de los ts_record
    min_ts = np.ones(n_ts)
    # todos los archivos
    lista_archivos = os.listdir(os.curdir)
    # contador auxiliar
    c = 0
    # loop para leer los records
    for archivo in lista_archivos:
        if archivo.startswith("ts_record"):
            # se lee el record
            record    = np.genfromtxt(archivo)
            # se busca el maximo
            max_ts[c] = record.max()
            # se busca el minimo
            min_ts[c] = record.min()
            c += 1
    # se compara los maximos con el archivo de datos de altura
    # contador auxiliar     
    k   = 0
    # inicializacion valores para marea
    val_bajamar = np.ones(n_ts)
    val_pleamar = np.ones(n_ts)
    # se restringe
    for i in xrange(n_ts):
        # localizar el punto de marea mas cercano
        idx_min_marea  = (np.abs(lat_marea - lat_ts[i])).argmin()
        # encontrar valores de marea mas adecuados
        val_bajamar[i] = bajamar[idx_min_marea]
        val_pleamar[i] = pleamar[idx_min_marea]
        if max_ts[i] < (altura[i] + val_pleamar[i] + tol_metros) and max_ts[i] < (altura[i] - val_bajamar[i] - tol_metros):
            k += 1
    # si pasa la restriccion dada la tolerancia, se agrega el directorio a la lista de modelos_ok
    if k >= (n_ts - tol):
        print(direc)
        modelos_ok.append(direc)
    os.chdir("..")


# se crea un archivo con todos los identificadores de los modelos que pasaron la restriccion
nombre_lista_idx = "lista_idx_modelos_restringidos_tsunami_LR.txt"
f = open(nombre_lista_idx,"w")
for idx in modelos_ok:
    f.write(str(idx)+"\n")
f.close()

# se copia los modelos restringidos al directorio de destino
for modelo in modelos_ok:
    id_modelo = modelo.split("_")[1] # se obtiene el identificador del modelo
    shutil.copy(dir_fallas+"/"+"deformacion_"+id_modelo+".tt3",dir_mods_rests) # copiar deformacion
    shutil.copy(dir_fallas+"/"+"falla_"+id_modelo+".npz",dir_mods_rests) # copiar slip
    shutil.copy(dir_fallas+"/"+"readme_"+id_modelo+".json",dir_mods_rests) # copiar ramas de arbol
os.chdir(dir_actual)