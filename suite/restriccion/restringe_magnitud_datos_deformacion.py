"""
ENCUENTRA LA FRANJA LATITUDINAL DONDE LOS DATOS DE DEFORMACION TIENEN MAYOR MAGNITUD Y RESTRINGE LOS MODELOS QUE NO TENGAN PARCHES EN LAS VECINDADES DE ESAS LATITUDES
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
# limites de franjas
limites_franjas = np.linspace(lat_lim_norte, lat_lim_sur, n_franjas+1)

"""
PARAMETROS DE RESTRICCION
"""
# tolerancia hacia el norte y sur en latitud del maximo dato de deformacion para encontrar el parche de slip
buffer_latitud = 0.2
# porcentaje de modelos restrinidos por cada franja de distancia con las franjas del rango
# ejemplo:
# rango:[1,2] 
# decaimiento de franja 0 sera 20 %, decaimiento de franja 4 sera 20x2=40 %
decaimiento    = 40

"""
INFO DE DIRECTORIOS
""" 
# directorio actual
dir_actual  = os.getcwd()
# directorio con datos de deformacion
dir_input   = "../input"
# directorio con modelos restringidos
ruta_slip   = "../fallas2/fallas2"
#meridionalmente1/modelos_restringidos_meridionalmente2/modelos_restringidos_meridionalmente3/modelos_restringidos_meridionalmente4"
# directorio destino
dir_destino = "modelos_restringidos_magnitud_datos"

"""
CARGAR BASE DE DATOS DE DEFORMACION
"""
# nombre archivo de datos
archivo_datos_deformacion = "def2_obs.xyz"
# cargar archivo
datos_deformacion = np.genfromtxt(dir_input+"/"+archivo_datos_deformacion, usecols = (0,1,2))
lon_datos         = datos_deformacion[:,0] - 360.0
lat_datos         = datos_deformacion[:,1]
deformacion_vert  = datos_deformacion[:,2]
abs_deformacion   = np.abs(deformacion_vert)
# Se asegura de que las latitudes de los datos de deformacion vaya de norte a sur
if np.diff(lat_datos).sum() < 0:
    lat_datos = np.sort(lat_datos)[::-1]
    lon_datos = lon_datos[np.argsort(lat_datos)]
    deformacion_vert = deformacion_vert[np.argsort(lat_datos)[::-1]]
    abs_deformacion  = abs_deformacion[np.argsort(lat_datos)[::-1]]


"""
ENCONTRAR LA FRANJA DONDE SE ENCUENTRA EL MAXIMO DE DEFORMACION
"""
max_magnitud_def   = abs_deformacion.max() # maxima magnitud (valor absoluto) de deformacion
lat_max_mag_def    = lat_datos[abs_deformacion==abs_deformacion.max()] # latitud del maximo de latitud
# indice de la franja donde se encuentra el maximo
idx_franja_max_mag = np.where(np.diff(limites_franjas < lat_max_mag_def))[0][0]
# de acuerdo al buffer definido arriba, se busca el rango norte y sur para encontrar el parche
lim_norte_rango    = lat_max_mag_def + buffer_latitud
lim_sur_rango      = lat_max_mag_def - buffer_latitud
# encontrar franjas donde se ubican los limites
idx_franja_lim_norte = np.where(np.diff(limites_franjas < lim_norte_rango))[0][0]
idx_franja_lim_sur = np.where(np.diff(limites_franjas < lim_sur_rango))[0][0]
# se crea una lista con todas las franjas en el rango
franjas_rango = np.arange(idx_franja_lim_norte, idx_franja_lim_sur+1, 1)


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
lista_modelos_aceptados           = [] # inicializacion de lista donde se guardara los nombres de los modelos restringidos (nuevo)
lista_modelos_noaceptados         = []
lista_franjas_modelos_aceptados   = []
lista_franjas_modelos_noaceptados = []
lista_aux = []
for modelo in lista_npz:
    idt         = modelo.split("_")[1].split(".")[0] # se extrae el codigo identificador de cada elemento
    print(idt)
    lista_aux = glob.glob("*_"+idt+".*")
    print(len(lista_aux))
    if len(lista_aux)!=3:
        continue
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
    peak_slip_idx, _ = find_peaks(slip_por_lat, prominence = 1) # peaks de slip separados por al menos 5 metros de diferencia
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
    # si el maximo no esta en el rango de franjas, quiere decir que se excluye el modelos
    if idx_franja in franjas_rango:
        lista_modelos_aceptados.append(idt) 
        lista_franjas_modelos_aceptados.append(numero_franja)
    else:
        lista_modelos_noaceptados.append(idt)
        lista_franjas_modelos_noaceptados.append(numero_franja)


"""
SAMPLEAR MODELOS Y COPIAR RESTRINGIR
"""
n_aceptados   = len(lista_modelos_aceptados) # cantidad de modelos que NO tienen el maximo en la franja a excluir
n_noaceptados = len(lista_modelos_noaceptados) # cantidad de modelos que SI tienen el maximo en la franja a excluir
# para cada modelo cuyo maximo no esta dentro del rango de franjas, se busca la distancia minima de la franja de su maximo al rango
# luego de acuerdo a la distancia y el valor de decaimiento, se obtiene un valor aleatorio con distribucion uniforme. Si este valor esta por sobre la probabilidad de decaimiento
# el modelo SERA restringido
c = 0 # contador auxiliar
id_mods_sampleados = []
for i in lista_franjas_modelos_noaceptados:
    distancia = np.abs(franjas_rango - i)
    distancia_minima = distancia.min()
    probabilidad = distancia_minima*decaimiento/100.0
    # valor aleatorio
    valor_random_test = np.random.uniform()
    if probabilidad < valor_random_test:
        id_mods_sampleados.append(lista_modelos_noaceptados[c])
    c += 1

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


nombre_lista_idx = "lista_idx_modelos_restringidos_magnitudesdeformacion.txt"
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
