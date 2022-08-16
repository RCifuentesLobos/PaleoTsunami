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
INFO DE DIRECTORIOS
"""
dir_fallas         = "../../../fallas2/fallas2/modelos_restringidos/modelos_restringidos_meridionalmente1/modelos_restringidos_meridionalmente2/modelos_restringidos_meridionalmente3/modelos_restringidos_meridionalmente4"
dir_modelaciones   = "../ctl_tsunami/modelacion_orden_ctdad_datos/castrodalcahue" # ruta al directorio donde se guardan los modelos
dir_input_altura   = "../input" # directorio donde se encuentra el archivo con altura
archivo_altura     = "alturaMaxenMetros2.txt" # archivo de datos de altura
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
LOOP DE RESTRICCION
"""
# lista donde se guardara los modelos que pasen las restricciones
modelos_ok = []
idx_orden = 15
# se corta el archivo de datos de acuerdo a cantidad de ts
lon    = lon[idx_orden:n_ts+idx_orden]
lat    = lat[idx_orden:n_ts+idx_orden]
altura = altura[idx_orden:n_ts+idx_orden]
# se va al directorio de modelaciones
os.chdir(dir_modelaciones)
# loop para ir por cada una de los directorios con datos
for direc in lista_dir_modelaciones:
    if direc.startswith("comcot"):
        os.chdir(direc)
        print(direc)
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
        # tolerancia
        tol = 0
        # contador auxiliar     
        k   = 0
        # se restringe
        for i in xrange(n_ts):
            if max_ts[i] > altura[i]:
                k += 1
        # si pasa la restriccion dada la tolerancia, se agrega el directorio a la lista de modelos_ok
        print(k)
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