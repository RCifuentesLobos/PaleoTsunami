import os
import glob
import shutil 
import random

# info de directorios
dir_fallas = "../fallas1/modelos_restringidos"
dir_mitad  = "mitad"
dir_tercio = "tercio"
dir_cuarto = "cuarto"
dir_actual = os.getcwd()

# crear lista con modelos 
os.chdir(dir_fallas)
# lista con todos los archivos npz sobre los que se iterara
lista_npz  = glob.glob("*.npz")       # lista con arrays de slip y coordenadas
n_modelos  = len(lista_npz)

# mitad de los modelos
mitad  = n_modelos//2
# tercio de los modelos
tercio = n_modelos//3
# cuarto de los modelos
cuarto = n_modelos//4

# crear lista sampleando aleatoriamente
lista_mitad  = random.sample(lista_npz, mitad)
lista_tercio  = random.sample(lista_npz, tercio)
lista_cuarto = random.sample(lista_npz, cuarto)

# listas con indices de modelos aleatorios
idx_mitad  = [i.split("_")[1].split(".")[0] for i in lista_mitad]
idx_tercio = [i.split("_")[1].split(".")[0] for i in lista_tercio]
idx_cuarto = [i.split("_")[1].split(".")[0] for i in lista_cuarto]

# copiar elementos
# mitad
for i in range(len(idx_mitad)):
    shutil.copy("deformacion_"+idx_mitad[i]+".tt3",dir_actual+"/"+dir_mitad) # copiar deformacion
    shutil.copy("falla_"+idx_mitad[i]+".npz",dir_actual+"/"+dir_mitad) # copiar slip
    shutil.copy("readme_"+idx_mitad[i]+".json",dir_actual+"/"+dir_mitad) # copiar ramas de arbol

for i in range(len(idx_tercio)):
    shutil.copy("deformacion_"+idx_tercio[i]+".tt3",dir_actual+"/"+dir_tercio) # copiar deformacion
    shutil.copy("falla_"+idx_tercio[i]+".npz",dir_actual+"/"+dir_tercio) # copiar slip
    shutil.copy("readme_"+idx_tercio[i]+".json",dir_actual+"/"+dir_tercio) # copiar ramas de arbol

for i in range(len(idx_cuarto)):
    shutil.copy("deformacion_"+idx_cuarto[i]+".tt3",dir_actual+"/"+dir_cuarto) # copiar deformacion
    shutil.copy("falla_"+idx_cuarto[i]+".npz",dir_actual+"/"+dir_cuarto) # copiar slip
    shutil.copy("readme_"+idx_cuarto[i]+".json",dir_actual+"/"+dir_cuarto) # copiar ramas de arbol