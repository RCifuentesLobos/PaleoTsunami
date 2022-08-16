"""
ENCUENTRA LA FRANJA LATITUDINAL DONDE UN MODELO PRESENTA SU MAXIMO SLIP Y RESTRINGE DE ACUERDO A SU POSICION
"""

import numpy as np 
import csv 
import random
import modfallas as mf 
import glob 
import os 
import shutil 
from scipy.signal import find_peaks, peak_prominences

"""
PARAMETROS DE FRANJAS LATITUDINALES
"""
lat_lim_norte = -36.0 # latitud limite norte de zona de ruptura
lat_lim_sur   = -46.0 # latitud limite sur de zona de ruptura
n_franjas     = 5     # cantidad de franjas que subdividiran la zona de ruptura
# franja que se quiere excluir
franja_excluir = 5 # NO es un indice, es el numero de la franja des 1 a n, indice seria franja_excluir - 1
# porcentaje de elementos a excluir
porcentaje_exclusion = 90

"""
CALCULO DE LIMITES DE FRANJAS
"""
limites_franjas = np.linspace(lat_lim_norte, lat_lim_sur, n_franjas+1)

"""
INFO DE DIRECTORIOS
""" 
# directorio actual
dir_actual  = os.getcwd()
# directorio con modelos restringidos
ruta_slip   = "../fallas2/modelos_restringidos/restriccion_fuerte/modelos_restringidos_meridionalmente1/modelos_restringidos_meridionalmente2/modelos_restringidos_meridionalmente3"
# directorio destino
dir_destino = "modelos_restringidos_meridionalmente4"


"""
CARGAR LISTAS
"""
os.chdir(ruta_slip)
# lista con todos los archivos npz sobre los que se iterara
lista_npz  = glob.glob("*.npz")       # lista con arrays de slip y coordenadas
lista_npz.sort(key=os.path.getctime)  
print("lista de npz cargada")

"""
CALCULO DE MAXIMOS Y SUS LATITUDES
"""
lista_modelos_aceptados    = [] # inicializacion de lista donde se guardara los nombres de los modelos restringidos (nuevo)
lista_modelos_noaceptados  = []
for modelo in lista_npz:
    idt         = modelo.split("_")[1].split(".")[0] # se extrae el codigo identificador de cada elemento
    slip_file   = 'falla_%s.npz' % (idt) # nombre archivo de falla asociado a d
    readme_file = 'readme_%s.json' % (idt)
    # cargar modelo aleatorio de slip
    data = np.load(modelo)
    # array con slip
    slip = data["Slip"]
    # array con latitudes
    lats          = data["array_lats"]
    lats_unicas   = np.unique(lats)  # latitudes unicas
    # se necesita que esten ordenadas de norte a sur
    if np.diff(lats_unicas).sum() > 0: # se chequea si array es creciente monotonicamente (ordenado de sur a norte)
        lats_unicas = lats_unicas[::-1]
    n_lats_unicas = len(lats_unicas) # cantidad de latitudes unicas
    # suma de slips por latitud
    slip_por_lat = slip.sum(axis=1)
    # indice maximos de slip
    peak_slip_idx, _ = find_peaks(slip_por_lat, prominence = 1 ) # peaks de slip separados por al menos 5 metros de diferencia
    # si hay un peak:
    if peak_slip_idx.size:   
        # prominencias de peaks de slip
        prom_peak_slip     = peak_prominences(slip_por_lat,peak_slip_idx)[0]
        max_prom_peak_slip = prom_peak_slip.max() # maxima prominencia
        idx_max_prom       = np.where(prom_peak_slip == max_prom_peak_slip)[0][0] # indice del peak mas prominente
        # latitudes de los peaks
        lats_peak_slip = lats_unicas[peak_slip_idx]
        # chequear en que franja latitudinal se encuentra
        idx_franja = np.where(np.diff(limites_franjas < lats_peak_slip[idx_max_prom]))[0][0] # indice de franja (de 0 a n-1)
    else:
        idx_max_lat  = np.where(slip_por_lat==slip_por_lat.max())[0][0]
        lat_max_slip = lats_unicas[idx_max_lat]
        # chequear en que franja latitudinal se encuentra
        idx_franja   = np.where(np.diff(limites_franjas < lat_max_slip))[0][0]
    numero_franja = idx_franja+1 # numero de franja (de 1 a n)
    # limites
    limite_norte = limites_franjas[idx_franja]
    limite_sur   = limites_franjas[idx_franja+1]
    # si no se encuentra el maximo en esa franja, quiere decir que no se excluye el modelo
    if numero_franja != franja_excluir:
        lista_modelos_aceptados.append(idt) # (nuevo)
    else:
        lista_modelos_noaceptados.append(idt)

"""
SAMPLEAR MODELOS Y COPIAR RESTRINGIR
"""
n_aceptados   = len(lista_modelos_aceptados) # cantidad de modelos que NO tienen el maximo en la franja a excluir
n_noaceptados = len(lista_modelos_noaceptados) # cantidad de modelos que SI tienen el maximo en la franja a excluir
# todos los modelos cuyo maximo no esta en la franja a excluir son copiados, del resto, se samplea aleatoriamente una cantidad 
n_sampleo     = int(n_noaceptados*porcentaje_exclusion/100)
# samplear 
id_mods_sampleados = random.sample(lista_modelos_noaceptados, n_sampleo)
# lista con elementos que pasan la restriccion
lista_final = lista_modelos_aceptados + id_mods_sampleados

for idt in lista_final:
    def_file    = 'deformacion_%s.tt3' % (idt)
    slip_file   = 'falla_%s.npz' % (idt) # nombre archivo de falla asociado a d
    readme_file = 'readme_%s.json' % (idt)

    shutil.copy(def_file,dir_destino)   # copiar elemento de deformacion
    shutil.copy(readme_file,dir_destino)
    shutil.copy(slip_file,dir_destino)
    print("copiado el modelo %s") % (idt)


nombre_lista_idx = "lista_idx_modelos_restringidos_meridionalmente.txt"
print(len(lista_final))
f = open(nombre_lista_idx,"w")
for idx in lista_final:
    f.write(str(idx)+"\n")
f.close()
shutil.copy(nombre_lista_idx,dir_destino)
print("Creada lista con identificadores de modelos restringidos")
print("Guardada en dir_destino")

#volver al directorio actual 
os.chdir(dir_actual)
