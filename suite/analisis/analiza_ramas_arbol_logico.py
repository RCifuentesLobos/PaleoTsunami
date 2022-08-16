import os
import glob
import shutil 
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gc 
from scipy.stats import mode
import json

gc.collect()

"""
PARAMETROS DE DIRECTORIO
"""
# directorio actual
dir_actual = os.getcwd()
# ruta directorio diccionarios
ruta_json = "../fallas2/modelos_restringidos"
os.chdir(ruta_json)
# ruta directorio figuras (relativo a directorio de modelos restringidos)
ruta_dir_figs = "../../figuras"


"""
CARGA DATOS
"""
# se crea una lista con los diccionarios con info de las ramas
lista_json = glob.glob("*.json")      # lista con diccionarios de parametros por modelo

"""
INICIALIZACION DE LISTAS PARA GUARDAR INFO DE RAMAS
"""
lista_mw = [] # magnitudes
lista_ar = [] # razones de aspecto
lista_ls = [] # limites norte
lista_ln = [] # limites sur
lista_N  = [] # complejidades

"""
LOOP PARA LEER INFO
"""

for i in lista_json:
    with open(i) as ramas:
        ramas_objeto = json.load(ramas)
        mw = ramas_objeto['Mw']
        ar = ramas_objeto['AR']
        ls = ramas_objeto['LS']
        ln = ramas_objeto['LN']
        N  = ramas_objeto['N']
        lista_mw.append(mw)
        lista_ar.append(ar)
        lista_ls.append(ls)
        lista_ln.append(ln)
        lista_N.append(N)
    ramas.close()

"""
GUARDAR REGISTRO DE PARAMETROS MAS PROBABLES
"""
# encontrar modas
moda_mw = mode(lista_mw)[0][0]
moda_ar = mode(lista_ar)[0][0]
moda_ln = mode(lista_ln)[0][0]
moda_ls = mode(lista_ls)[0][0]
moda_N  = mode(lista_N)[0][0]
# crear json con modelos mas probables
dict_mas_prob = {"Mw": moda_mw,
                 "ar": moda_ar,
                 "LN": moda_ln,
                 "LS": moda_ls,
                 "N":  moda_N
}
archivo_parametros_al = "parametros_AL_mas_probables.json"
json_mas_prob = json.dumps(dict_mas_prob)
json_archivo  = open(archivo_parametros_al, 'w')
json_archivo.write(json_mas_prob)
json_archivo.close()

"""
GRAFICOS
"""
# histograma magnitudes

n, bins, patches = plt.hist(x=lista_mw, bins='auto', color='#0504aa',
                            alpha=0.7)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Mw')
plt.ylabel('Frequency')
plt.title('Magnitude frequency')
plt.savefig('histo_mags.png', transparent = True)

# histograma razones de aspecto

n, bins, patches = plt.hist(x=lista_ar, bins='auto', color='#0504aa',
                            alpha=0.7)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Southern limit')
plt.ylabel('Frequency')
plt.title('Aspect ratio frequency')
plt.savefig('histo_ar.png', transparent = True)


# histograma limite sur

n, bins, patches = plt.hist(x=lista_ls, bins='auto', color='#0504aa',
                            alpha=0.7)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Southern limit')
plt.ylabel('Frequency')
plt.title('Southern limit frequency')
plt.savefig('histo_ls.png', transparent = True)

# histograma limite norte

n, bins, patches = plt.hist(x=lista_ln, bins='auto', color='#0504aa',
                            alpha=0.7)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Southern limit')
plt.ylabel('Frequency')
plt.title('Northern limit frequency')
plt.savefig('histo_ln.png', transparent = True)

# mover figuras
lista_figs = glob.glob("*.png")
for fig in lista_figs:
    shutil.move(fig, ruta_dir_figs)

# volver al directorio principal
os.chdir(dir_actual)