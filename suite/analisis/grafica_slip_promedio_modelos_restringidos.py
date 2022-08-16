import os
import glob
import shutil 
import sys
import json
import numpy as np
from scipy.stats import mode
import modokada as mo 
import modfallas as mf 
import csv
import modrestricciones as mr
from mpl_toolkits.basemap import Basemap, cm
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from scipy.interpolate import RegularGridInterpolator, interp1d, interp2d ,griddata, Rbf
from geographiclib.geodesic import Geodesic
import gc 

gc.collect()


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
ruta_slip = ["../" + i + "/modelos_restringidos" for i in lista_dir_salidas]
ruta_slip = ruta_slip[1:n_dir_salidas]
# ruta directorio figuras (relativo a directorio de modelos restringidos)
ruta_dir_figs = "../../figuras"

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
LOOP PARA CALCULAR PROMEDIO Y GRAFICAR
"""

# inicializar matriz de calculo de promedio
ini_data        = np.load(lista_npz[0])
array_prom_slip = np.zeros(ini_data["Slip"].shape)
# inicializar matriz de calculo de moda
array_slips = np.zeros( ini_data["Slip"].shape + (len(lista_npz),) )

# coordenadas
lons = ini_data["array_lons"]
lats = ini_data["array_lats"]



for i in range(len(lista_npz)):
    data = np.load(lista_npz[i])
    slip = data["Slip"]
    array_prom_slip += slip
    array_slips[:,:,i] = slip

# promedio
array_prom_slip /= len(lista_npz)
# moda
moda_slip    = np.squeeze(mode(array_slips, axis=2)[0]) 
# mediana
mediana_slip = np.median(array_slips, axis=2)

# calculo de estadisticos con loops
# inicializacion de arrays
array_prom_slip_loop   = np.zeros(ini_data["Slip"].shape)
array_moda_slip_loop   = np.zeros(ini_data["Slip"].shape)
array_median_slip_loop = np.zeros(ini_data["Slip"].shape)
# moda con loop
for i in range(np.shape(array_slips)[0]):
    for j in range(np.shape(array_slips)[1]):
        array_prom_slip_loop[i,j]   = np.mean(array_slips[i,j,:])
        #array_moda_slip_loop[i,j]   = mode(array_slips[i,j,:])
        array_median_slip_loop[i,j] = np.median(array_slips[i,j,:])


"""
FIGURAS
"""


"""
PROMEDIO
"""

# fig = plt.figure()
# ax = fig.add_subplot(111)
# cs = ax.contourf(lons,lats,array_prom_slip)
# ax.contour(cs, colors='k') 
# ax.set_ylim((np.min(lats)-0.5,np.max(lats)+0.5))
# cbar = plt.colorbar(cs)
# cbar.set_label('Av. slip [m]')
# plt.savefig('slip_ave3.png', transparent = True)
# #plt.show() 


fig = plt.figure()
ax = fig.add_subplot(111)
# iniciliazar mapa
m = Basemap(projection='merc', ax=ax, lat_0=35, lon_0=210,
    resolution = 'h',
    llcrnrlon=-78, llcrnrlat=-46,
    urcrnrlon=-70, urcrnrlat=-36)
# transformar coordenadas geograficas a coord de mapa
mlons, mlats         = m(lons, lats)
mfosalons, mfosalats = m(lonfosa, latfosa)
# promedio
csave = m.pcolormesh(mlons, mlats, array_prom_slip)
cbar     = m.colorbar(csave,location='bottom',pad="5%")
cbar.set_label('m')
# anexos
m.plot(mfosalons, mfosalats, marker=None, color='k')
m.drawcoastlines()
m.drawcountries(linewidth=0.25)
m.drawmeridians(np.arange(-180,180,2),labels=[1,1,0,1])
m.drawparallels(np.arange(-50,-30,2),labels=[1,1,0,1])
plt.title('Average')
plt.savefig('mapa_slip_ave_restriccion_fuerte.png', transparent = True, bbox_inches='tight', pad_inches=0)

"""
MODA
"""

# fig = plt.figure()
# ax = fig.add_subplot(111)
# cs = ax.contourf(lons,lats,moda_slip)
# ax.contour(cs, colors='k') 
# ax.set_ylim((np.min(lats)-0.5,np.max(lats)+0.5))
# cbar = plt.colorbar(cs)
# cbar.set_label('Mode slip [m]')
# plt.savefig('slip_mode3.png', transparent = True)
# #plt.show() 

# inicializar plot
fig = plt.figure()
ax = fig.add_subplot(111)
# iniciliazar mapa
m = Basemap(projection='merc', ax=ax, lat_0=35, lon_0=210,
    resolution = 'h',
    llcrnrlon=-78, llcrnrlat=-46,
    urcrnrlon=-70, urcrnrlat=-36)
# transformar coordenadas geograficas a coord de mapa
mlons, mlats         = m(lons, lats)
mfosalons, mfosalats = m(lonfosa, latfosa)
# moda
csmoda = m.pcolormesh(mlons, mlats, moda_slip)
cbar = m.colorbar(csmoda,location='bottom',pad="5%")
cbar.set_label('m')
# anexos
m.plot(mfosalons, mfosalats, marker=None, color='k')
m.drawcoastlines()
m.drawcountries(linewidth=0.25)
m.drawmeridians(np.arange(-180,180,2),labels=[1,1,0,1])
m.drawparallels(np.arange(-50,-30,2),labels=[1,1,0,1])
plt.title('Mode')
plt.savefig('mapa_slip_mode_restriccion_fuerte.png', transparent = True, bbox_inches='tight', pad_inches=0)

"""
MEDIANA
"""

# fig = plt.figure()
# ax = fig.add_subplot(111)
# cs = ax.contourf(lons,lats,mediana_slip)
# ax.contour(cs, colors='k') 
# ax.set_ylim((np.min(lats)-0.5,np.max(lats)+0.5))
# cbar = plt.colorbar(cs)
# cbar.set_label('Median slip [m]')
# plt.savefig('slip_median3.png', transparent = True)
# #plt.show() 


fig = plt.figure()
ax = fig.add_subplot(111)
# iniciliazar mapa
m = Basemap(projection='merc', ax=ax, lat_0=35, lon_0=210,
    resolution = 'h',
    llcrnrlon=-78, llcrnrlat=-46,
    urcrnrlon=-70, urcrnrlat=-36)
# transformar coordenadas geograficas a coord de mapa
mlons, mlats         = m(lons, lats)
mfosalons, mfosalats = m(lonfosa, latfosa)
# moda
csmedian = m.pcolormesh(mlons, mlats, mediana_slip)
cbar     = m.colorbar(csmedian,location='bottom',pad="5%")
cbar.set_label('m')
# anexos
m.plot(mfosalons, mfosalats, marker=None, color='k')
m.drawcoastlines()
m.drawcountries(linewidth=0.25)
m.drawmeridians(np.arange(-180,180,2),labels=[1,1,0,1])
m.drawparallels(np.arange(-50,-30,2),labels=[1,1,0,1])
plt.title('Median')
plt.savefig('mapa_slip_median_restriccion_fuerte.png', transparent = True, bbox_inches='tight', pad_inches=0)





# mover figuras
lista_figs = glob.glob("*.png")
for fig in lista_figs:
    shutil.move(fig, dir_actual)


os.chdir(dir_actual)


# guardar csv media
out=np.column_stack((lons.ravel(), lats.ravel(), array_prom_slip.ravel()))
nombre_archivo = "media_restriccion_fuerte.csv"
with open(nombre_archivo,"w") as f:
    writer = csv.writer(f)
    writer.writerows(out)

# guardar csv moda
out=np.column_stack((lons.ravel(), lats.ravel(), moda_slip.ravel()))
nombre_archivo = "moda_restriccion_fuerte.csv"
with open(nombre_archivo,"w") as f:
    writer = csv.writer(f)
    writer.writerows(out)

# guardar csv mediana
out=np.column_stack((lons.ravel(), lats.ravel(), mediana_slip.ravel()))
nombre_archivo = "mediana_restriccion_fuerte.csv"
with open(nombre_archivo,"w") as f:
    writer = csv.writer(f)
    writer.writerows(out)