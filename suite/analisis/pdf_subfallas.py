import os
import glob
import shutil 
import sys
import json
import csv
import modfallas as mf 
import pandas as pd
import numpy as np
from scipy.stats import mode
from scipy.stats import lognorm
from mpl_toolkits.basemap import Basemap, cm
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator, interp1d, interp2d ,griddata, Rbf


"""
PARAMETROS DE DIRECTORIO
"""
# directorio actual
dir_actual = os.getcwd()
# directorio con directorios de salidas
directorio_salidas  = "../" 
# ruta directorio diccionarios
nombre_salidas_gral = "fallas"    # nonbre de los n subdirectorios con salidas
# lista de directorios con salidas
lista_dir_salidas = list(filter( lambda x: x.startswith(nombre_salidas_gral), os.listdir(directorio_salidas)))
lista_dir_salidas[:] = [ i for i in lista_dir_salidas ]
# cantidad de directorios
n_dir_salidas = len(lista_dir_salidas)
ruta_slip = ["../" + i + "/modelos_restringidos/restriccion_fuerte" for i in lista_dir_salidas]
#ruta_slip = ruta_slip[1:n_dir_salidas]
# ruta directorio figuras (relativo a directorio de modelos restringidos)
ruta_dir_figs = "../../../figuras"

"""
CARGAR FOSA
"""

# ruta del archivo de la fosa
ruta_fosa = "../Slab/"
# archivo fosa ( primera columna: longitudes, segunda columna: latitudes)
arc_fosa  = ruta_fosa + "SAM3.txt"
# carga de fosa usando funcion del modulo modfallas
lonfosa, latfosa  = mf.carga_fosa(arc_fosa)

"""
IR A DIRECTORIO DE TRABAJO
"""
os.chdir(ruta_slip[2])

"""
CARGAR LISTAS
"""
# lista con todos los archivos npz sobre los que se iterara
lista_npz  = glob.glob("*.npz")       # lista con arrays de slip y coordenadas
lista_npz.sort(key=os.path.getctime)  


"""
LOOP PARA OBTENER PDF
"""

# inicializar matrices de segmentos
ini_data = np.load(lista_npz[2])
# coordenadas
lons = ini_data["array_lons"]
lats = ini_data["array_lats"]
# tamano array
dim_array = np.asarray(np.shape(lons))

#inicializar array con valores de distribuciones de slip
array_slips_todos = np.ones((len(lista_npz),dim_array[0],dim_array[1]))


# se leen todos los archivos de slip
for s in xrange(len(lista_npz)):
    # se carga el slip
    data = np.load(lista_npz[s])
    slip = data["Slip"]
    array_slips_todos[s,:,:] = slip
    print(lista_npz[s])


# inicializar array para los valores mas probables de slip
slip_max_pdf = np.ones(dim_array)
# se calculan los pdf por subfalla
for i in xrange(dim_array[0]):
    for j in xrange(dim_array[1]):
        x                 = array_slips_todos[:,i,j]
        tam               = np.size(slip_max_pdf)
        n, bins, patches  = plt.hist(x,len(x),density=True)
        idx_max_pdf       = n.argmax()
        slip_max_pdf[i,j] = x[idx_max_pdf]
        print(i)
        print(j)
        del n
        del bins
        del patches

with open('resolucion_max_pdf_restriccion_fuerte.npy','wb') as f:
    np.save(f, slip_max_pdf)


fig = plt.figure()
ax = fig.add_subplot(111)
# iniciliazar mapa
m = Basemap(projection='merc', ax=ax, lat_0=35, lon_0=210,
    resolution = 'h',
    llcrnrlon=-78, llcrnrlat=-46,
    urcrnrlon=-70, urcrnrlat=-38)
# transformar coordenadas geograficas a coord de mapa
mlons, mlats         = m(lons, lats)
mfosalons, mfosalats = m(lonfosa, latfosa)
# promedio
csave = m.pcolormesh(mlons, mlats, slip_max_pdf)
cbar     = m.colorbar(csave,location='bottom',pad="5%")
cbar.set_label('m')
# anexos
m.plot(mfosalons, mfosalats, marker=None, color='k')
m.drawcoastlines()
m.drawcountries(linewidth=0.25)
m.drawmeridians(np.arange(-180,180,2),labels=[1,1,0,1])
m.drawparallels(np.arange(-50,-30,2),labels=[1,1,0,1])
plt.title('Estimated slip')
plt.savefig('maxpdf_fallas3_resolucion2_coincidencias_v2.png', transparent = True, bbox_inches='tight', pad_inches=0)
