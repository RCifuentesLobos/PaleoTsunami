import numpy as np 
import os
import glob 
import modfallas as mf
import modokada as mo
import csv
import shutil

"""
CREA ARCHIVOS CSV A PARTIR DE LOS ARCHIVOS RESTRINGIDOS
"""

dir_actual  = os.getcwd()
path_slip="../fallas/modelos_restringidos"
os.chdir(path_slip)
dir_destino = "csv_files"
"""
CARGAR LISTAS
"""
# lista con todos los archivos npz sobre los que se iterara
lista_npz  = glob.glob("*.npz")       # lista con arrays de slip y coordenadas
lista_npz.sort(key=os.path.getctime)  # lista ordenada
lista_json = glob.glob("*.json")      # lista con diccionarios de parametros por modelo
lista_json.sort(key=os.path.getctime) # lista ordenada
lista_def = glob.glob("*.tt3")        # lista con info de deformacion 
lista_def.sort(key=os.path.getctime)  # lista ordenada
lista_idx_rest = np.genfromtxt("lista_idx_modelos_restringidos.txt") # lista con los id de los modelos originales que pasaron la restriccion

"""
LOOP DE TRANSFORMACION A CSV
"""

# contador auxiliar
c = 0 
k = 0
for s in lista_npz:    
    # matriz donde se guardara la deformacion para el calculo del promedio
    data_falla_n = np.load(s)
    lonsslip     = data_falla_n["array_lons"]
    latsslip     = data_falla_n["array_lats"]
    slip         = data_falla_n["Slip"]
    data = np.stack([lonsslip.ravel(), latsslip.ravel(), slip.ravel()],axis = 1)
    nombre_archivo = "slip_%d.csv" %(lista_idx_rest[c]) 
    c += 1
    k += 1 # se cuenta la cantidad de archivos sumados
    with open(nombre_archivo,"w") as f:
        writer = csv.writer(f)
        writer.writerows(data)
    print(k)
    print(nombre_archivo)
    shutil.copy(nombre_archivo,dir_destino)


# eliminar archivos.csv en directorio path_deformacion para evitar duplicados
lista_csv_dir_actual = glob.glob("*.csv")
for csv in lista_csv_dir_actual:
    os.remove(csv)
print("Modelos transformados a .csv y copiados a directorio dir_destino")

os.chdir(dir_actual)
