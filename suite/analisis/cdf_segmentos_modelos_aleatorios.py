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
DEFINCION ECDF
"""
def ecdf(x):
    xs = np.sort(x)
    ys = np.arange(1, len(xs)+1)/float(len(xs))
    return xs, ys

"""
LOOP PARA CALCULAR PROMEDIO Y GRAFICAR
"""

# inicializar matrices de segmentos
ini_data = np.load(lista_npz[2])
# coordenadas
lons = ini_data["array_lons"]
lats = ini_data["array_lats"]
# tamano array
dim_array = np.asarray(np.shape(lons))
# # array con cdf de toda la falla en general
# xcdf_falla_completa = np.zeros((len(lons.ravel()),len(lista_npz)))
# ycdf_falla_completa = np.zeros((len(lons.ravel()),len(lista_npz)))


# """
# CALCULO ECDF
# """

# for i in range(len(lista_npz)):
#     data         = np.load(lista_npz[i])
#     slip         = data["Slip"]
#     xcdf_falla_completa[:,i], ycdf_falla_completa[:,i] = ecdf(slip.ravel())

# """
# ENCONTRAR VALORES EN PERCENTIL 50, 75 Y 90
# """
# # funcion para encontrar valores en dichos percentiles
# def find_nearest(array, value):
#     array = np.asarray(array)
#     idx = (np.abs(array - value)).argmin()
#     return array[idx]

# # inicializar arrays con valores para percentiles
# slip_perc_50 = np.zeros((len(lista_npz)))
# slip_perc_75 = np.zeros((len(lista_npz)))
# slip_perc_90 = np.zeros((len(lista_npz)))

# # loop para encontrar valores
# for i in range(len(lista_npz)):
#     idx50        = np.abs(ycdf_falla_completa[:,i] - 0.5).argmin()
#     idx75        = np.abs(ycdf_falla_completa[:,i] - 0.75).argmin()
#     idx90        = np.abs(ycdf_falla_completa[:,i] - 0.9).argmin()
#     slip_perc_50[i] = xcdf_falla_completa[idx50,i]
#     slip_perc_75[i] = xcdf_falla_completa[idx75,i]
#     slip_perc_90[i] = xcdf_falla_completa[idx90,i]
# # encontrar valores

"""
CREACION DE DIVISIONES DE LA FALLA
"""
# se divide la falla en 5 segmento de norte a sur y en 3 de oeste a este, resultando 15 segmentos
#inicializar 15 segmentos
norte_a       = []
norte_b       = []
norte_c       = []
centronorte_a = []
centronorte_b = []
centronorte_c = []
centro_a      = []
centro_b      = []
centro_c      = []
centrosur_a   = []
centrosur_b   = []
centrosur_c   = []
sur_a         = []
sur_b         = []
sur_c         = []


xnorte_a_cdf, xcentronorte_a_cdf, xcentro_a_cdf, xcentrosur_a_cdf, xsur_a_cdf = [np.zeros((16*6,len(lista_npz))) for i in range(5)]
ynorte_a_cdf, ycentronorte_a_cdf, ycentro_a_cdf, ycentrosur_a_cdf, ysur_a_cdf = [np.zeros((16*6,len(lista_npz))) for i in range(5)]
xnorte_b_cdf, xcentronorte_b_cdf, xcentro_b_cdf, xcentrosur_b_cdf, xsur_b_cdf = [np.zeros((16*7,len(lista_npz))) for i in range(5)]
ynorte_b_cdf, ycentronorte_b_cdf, ycentro_b_cdf, ycentrosur_b_cdf, ysur_b_cdf = [np.zeros((16*7,len(lista_npz))) for i in range(5)]
xnorte_c_cdf, xcentronorte_c_cdf, xcentro_c_cdf, xcentrosur_c_cdf, xsur_c_cdf = [np.zeros((16*7,len(lista_npz))) for i in range(5)]
ynorte_c_cdf, ycentronorte_c_cdf, ycentro_c_cdf, ycentrosur_c_cdf, ysur_c_cdf = [np.zeros((16*7,len(lista_npz))) for i in range(5)]

# loop de calculo de ecdf
for s in range(len(lista_npz)):
    # se carga el slip
    data = np.load(lista_npz[s])
    slip = data["Slip"]
    # se subdivide en secciones
    for i in xrange(dim_array[0]):
        for j in xrange(dim_array[1]):
            if   ( (i>=0)  and (i<=15) and (j>=0)  and (j<=5) ):
                norte_a.append(slip[i,j])
            elif ( (i>=16) and (i<=31) and (j>=0)  and (j<=5) ):
                centronorte_a.append(slip[i,j])
            elif ( (i>=32) and (i<=47) and (j>=0)  and (j<=5) ):
                centro_a.append(slip[i,j])
            elif ( (i>=48) and (i<=63) and (j>=0)  and (j<=5) ):
                centrosur_a.append(slip[i,j])
            elif ( (i>=64) and (i<=79) and (j>=0)  and (j<=5) ):    
                sur_a.append(slip[i,j])
            elif ( (i>=0)  and (i<=15) and (j>=6)  and (j<=12) ):
                norte_b.append(slip[i,j])
            elif ( (i>=16) and (i<=31) and (j>=6)  and (j<=12) ):
                centronorte_b.append(slip[i,j])
            elif ( (i>=32) and (i<=47) and (j>=6)  and (j<=12) ):
                centro_b.append(slip[i,j])
            elif ( (i>=48) and (i<=63) and (j>=6)  and (j<=12) ):
                centrosur_b.append(slip[i,j])
            elif ( (i>=64) and (i<=79) and (j>=6)  and (j<=12) ):    
                sur_b.append(slip[i,j])
            elif ( (i>=0)  and (i<=15) and (j>=13) and (j<=19) ):
                norte_c.append(slip[i,j])
            elif ( (i>=16) and (i<=31) and (j>=13) and (j<=19) ):
                centronorte_c.append(slip[i,j])
            elif ( (i>=32) and (i<=47) and (j>=13) and (j<=19) ):
                centro_c.append(slip[i,j])
            elif ( (i>=48) and (i<=63) and (j>=13) and (j<=19) ):
                centrosur_c.append(slip[i,j])
            elif ( (i>=64) and (i<=79) and (j>=13) and (j<=19) ):
                sur_c.append(slip[i,j])
    print(lista_npz[s])
    # calculo de ecdf
    # segmento A (superficial)
    xnorte_a_cdf[:,s],       ynorte_a_cdf[:,s]       = ecdf(norte_a)
    xcentronorte_a_cdf[:,s], ycentronorte_a_cdf[:,s] = ecdf(centronorte_a)
    xcentro_a_cdf[:,s],      ycentro_a_cdf[:,s]      = ecdf(centro_a)
    xcentrosur_a_cdf[:,s],   ycentrosur_a_cdf[:,s]   = ecdf(centrosur_a)
    xsur_a_cdf[:,s],         ysur_a_cdf[:,s]         = ecdf(sur_a)
    # segmento B (centro)
    xnorte_b_cdf[:,s],       ynorte_b_cdf[:,s]       = ecdf(norte_b)
    xcentronorte_b_cdf[:,s], ycentronorte_b_cdf[:,s] = ecdf(centronorte_b)
    xcentro_b_cdf[:,s],      ycentro_b_cdf[:,s]      = ecdf(centro_b)
    xcentrosur_b_cdf[:,s],   ycentrosur_b_cdf[:,s]   = ecdf(centrosur_b)
    xsur_b_cdf[:,s],         ysur_b_cdf[:,s]         = ecdf(sur_b)
    # segmento C (profundo)
    xnorte_c_cdf[:,s],       ynorte_c_cdf[:,s]       = ecdf(norte_c)
    xcentronorte_c_cdf[:,s], ycentronorte_c_cdf[:,s] = ecdf(centronorte_c)
    xcentro_c_cdf[:,s],      ycentro_c_cdf[:,s]      = ecdf(centro_c)
    xcentrosur_c_cdf[:,s],   ycentrosur_c_cdf[:,s]   = ecdf(centrosur_c)
    xsur_c_cdf[:,s],         ysur_c_cdf[:,s]         = ecdf(sur_c)
    # se limpian las listas
    norte_a       = []
    norte_b       = []
    norte_c       = []
    centronorte_a = []
    centronorte_b = []
    centronorte_c = []
    centro_a      = []
    centro_b      = []
    centro_c      = []
    centrosur_a   = []
    centrosur_b   = []
    centrosur_c   = []
    sur_a         = []
    sur_b         = []
    sur_c         = []

"""
ESTIMACIONES DE PERCENTILES POR SEGMENTO
"""
# inicializacion de arrays
p50_norte_a, p50_norte_b, p50_norte_c, p50_centronorte_a, p50_centronorte_b, p50_centronorte_c, p50_centro_a, p50_centro_b, p50_centro_c, p50_centrosur_a, p50_centrosur_b, p50_centrosur_c, p50_sur_a, p50_sur_b, p50_sur_c = [np.zeros((len(lista_npz))) for i in range(15)]
p75_norte_a, p75_norte_b, p75_norte_c, p75_centronorte_a, p75_centronorte_b, p75_centronorte_c, p75_centro_a, p75_centro_b, p75_centro_c, p75_centrosur_a, p75_centrosur_b, p75_centrosur_c, p75_sur_a, p75_sur_b, p75_sur_c = [np.zeros((len(lista_npz))) for i in range(15)]
p90_norte_a, p90_norte_b, p90_norte_c, p90_centronorte_a, p90_centronorte_b, p90_centronorte_c, p90_centro_a, p90_centro_b, p90_centro_c, p90_centrosur_a, p90_centrosur_b, p90_centrosur_c, p90_sur_a, p90_sur_b, p90_sur_c = [np.zeros((len(lista_npz))) for i in range(15)]

# loop para encontrar los percentiles
for i in xrange(len(lista_npz)):
    print(lista_npz[i])
    # indices percentiles
    # 50
    idx50an   =  np.abs(ynorte_a_cdf[:,i] - 0.5).argmin()
    idx50bn   =  np.abs(ynorte_b_cdf[:,i] - 0.5).argmin()
    idx50cn   =  np.abs(ynorte_c_cdf[:,i] - 0.5).argmin()
    idx50acn  =  np.abs(ycentronorte_a_cdf[:,i] - 0.5).argmin()
    idx50bcn  =  np.abs(ycentronorte_b_cdf[:,i] - 0.5).argmin()
    idx50ccn  =  np.abs(ycentronorte_c_cdf[:,i] - 0.5).argmin()
    idx50ac   =  np.abs(ycentro_a_cdf[:,i] - 0.5).argmin()
    idx50bc   =  np.abs(ycentro_b_cdf[:,i] - 0.5).argmin()
    idx50cc   =  np.abs(ycentro_c_cdf[:,i] - 0.5).argmin()
    idx50acs  =  np.abs(ycentrosur_a_cdf[:,i] - 0.5).argmin()
    idx50bcs  =  np.abs(ycentrosur_b_cdf[:,i] - 0.5).argmin()
    idx50ccs  =  np.abs(ycentrosur_c_cdf[:,i] - 0.5).argmin()
    idx50as   =  np.abs(ysur_a_cdf[:,i] - 0.5).argmin()
    idx50bs   =  np.abs(ysur_b_cdf[:,i] - 0.5).argmin()
    idx50cs   =  np.abs(ysur_c_cdf[:,i] - 0.5).argmin()
    # 75
    idx75an   =  np.abs(ynorte_a_cdf[:,i] - 0.75).argmin()
    idx75bn   =  np.abs(ynorte_b_cdf[:,i] - 0.75).argmin()
    idx75cn   =  np.abs(ynorte_c_cdf[:,i] - 0.75).argmin()
    idx75acn  =  np.abs(ycentronorte_a_cdf[:,i] - 0.75).argmin()
    idx75bcn  =  np.abs(ycentronorte_b_cdf[:,i] - 0.75).argmin()
    idx75ccn  =  np.abs(ycentronorte_c_cdf[:,i] - 0.75).argmin()
    idx75ac   =  np.abs(ycentro_a_cdf[:,i] - 0.75).argmin()
    idx75bc   =  np.abs(ycentro_b_cdf[:,i] - 0.75).argmin()
    idx75cc   =  np.abs(ycentro_c_cdf[:,i] - 0.75).argmin()
    idx75acs  =  np.abs(ycentrosur_a_cdf[:,i] - 0.75).argmin()
    idx75bcs  =  np.abs(ycentrosur_b_cdf[:,i] - 0.75).argmin()
    idx75ccs  =  np.abs(ycentrosur_c_cdf[:,i] - 0.75).argmin()
    idx75as   =  np.abs(ysur_a_cdf[:,i] - 0.75).argmin()
    idx75bs   =  np.abs(ysur_b_cdf[:,i] - 0.75).argmin()
    idx75cs   =  np.abs(ysur_c_cdf[:,i] - 0.75).argmin()
    # 50
    idx90an   =  np.abs(ynorte_a_cdf[:,i] - 0.9).argmin()
    idx90bn   =  np.abs(ynorte_b_cdf[:,i] - 0.9).argmin()
    idx90cn   =  np.abs(ynorte_c_cdf[:,i] - 0.9).argmin()
    idx90acn  =  np.abs(ycentronorte_a_cdf[:,i] - 0.9).argmin()
    idx90bcn  =  np.abs(ycentronorte_b_cdf[:,i] - 0.9).argmin()
    idx90ccn  =  np.abs(ycentronorte_c_cdf[:,i] - 0.9).argmin()
    idx90ac   =  np.abs(ycentro_a_cdf[:,i] - 0.9).argmin()
    idx90bc   =  np.abs(ycentro_b_cdf[:,i] - 0.9).argmin()
    idx90cc   =  np.abs(ycentro_c_cdf[:,i] - 0.9).argmin()
    idx90acs  =  np.abs(ycentrosur_a_cdf[:,i] - 0.9).argmin()
    idx90bcs  =  np.abs(ycentrosur_b_cdf[:,i] - 0.9).argmin()
    idx90ccs  =  np.abs(ycentrosur_c_cdf[:,i] - 0.9).argmin()
    idx90as   =  np.abs(ysur_a_cdf[:,i] - 0.9).argmin()
    idx90bs   =  np.abs(ysur_b_cdf[:,i] - 0.9).argmin()
    idx90cs   =  np.abs(ysur_c_cdf[:,i] - 0.9).argmin()
    # obtencion slip para percetniles
    # 50
    p50_norte_a[i]       = xnorte_a_cdf[idx50an,i]
    p50_norte_b[i]       = xnorte_b_cdf[idx50bn,i]
    p50_norte_c[i]       = xnorte_c_cdf[idx50cn,i]
    p50_centronorte_a[i] = xcentronorte_a_cdf[idx50acn,i]
    p50_centronorte_b[i] = xcentronorte_b_cdf[idx50bcn,i]
    p50_centronorte_c[i] = xcentronorte_c_cdf[idx50ccn,i]
    p50_centro_a[i]      = xcentro_a_cdf[idx50ac,i]
    p50_centro_b[i]      = xcentro_b_cdf[idx50bc,i]
    p50_centro_c[i]      = xcentro_c_cdf[idx50cc,i]
    p50_centrosur_a[i]   = xcentrosur_a_cdf[idx50acs,i]
    p50_centrosur_b[i]   = xcentrosur_b_cdf[idx50bcs,i]
    p50_centrosur_c[i]   = xcentrosur_c_cdf[idx50ccs,i]
    p50_sur_a[i]         = xsur_a_cdf[idx50as,i]
    p50_sur_b[i]         = xsur_b_cdf[idx50bs,i]
    p50_sur_c[i]         = xsur_c_cdf[idx50cs,i]
    # 75
    p75_norte_a[i]       = xnorte_a_cdf[idx75an,i]
    p75_norte_b[i]       = xnorte_b_cdf[idx75bn,i]
    p75_norte_c[i]       = xnorte_c_cdf[idx75cn,i]
    p75_centronorte_a[i] = xcentronorte_a_cdf[idx75acn,i]
    p75_centronorte_b[i] = xcentronorte_b_cdf[idx75bcn,i]
    p75_centronorte_c[i] = xcentronorte_c_cdf[idx75ccn,i]
    p75_centro_a[i]      = xcentro_a_cdf[idx75ac,i]
    p75_centro_b[i]      = xcentro_b_cdf[idx75bc,i]
    p75_centro_c[i]      = xcentro_c_cdf[idx75cc,i]
    p75_centrosur_a[i]   = xcentrosur_a_cdf[idx75acs,i]
    p75_centrosur_b[i]   = xcentrosur_b_cdf[idx75bcs,i]
    p75_centrosur_c[i]   = xcentrosur_c_cdf[idx75ccs,i]
    p75_sur_a[i]         = xsur_a_cdf[idx75as,i]
    p75_sur_b[i]         = xsur_b_cdf[idx75bs,i]
    p75_sur_c[i]         = xsur_c_cdf[idx75cs,i]
    # 50s
    p90_norte_a[i]       = xnorte_a_cdf[idx90an,i]
    p90_norte_b[i]       = xnorte_b_cdf[idx90bn,i]
    p90_norte_c[i]       = xnorte_c_cdf[idx90cn,i]
    p90_centronorte_a[i] = xcentronorte_a_cdf[idx90acn,i]
    p90_centronorte_b[i] = xcentronorte_b_cdf[idx90bcn,i]
    p90_centronorte_c[i] = xcentronorte_c_cdf[idx90ccn,i]
    p90_centro_a[i]      = xcentro_a_cdf[idx90ac,i]
    p90_centro_b[i]      = xcentro_b_cdf[idx90bc,i]
    p90_centro_c[i]      = xcentro_c_cdf[idx90cc,i]
    p90_centrosur_a[i]   = xcentrosur_a_cdf[idx90acs,i]
    p90_centrosur_b[i]   = xcentrosur_b_cdf[idx90bcs,i]
    p90_centrosur_c[i]   = xcentrosur_c_cdf[idx90ccs,i]
    p90_sur_a[i]         = xsur_a_cdf[idx90as,i]
    p90_sur_b[i]         = xsur_b_cdf[idx90bs,i]
    p90_sur_c[i]         = xsur_c_cdf[idx90cs,i]
"""
GRAFICOS
"""
print('graficando...')
os.chdir(dir_actual)
# # percentil 50
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.hist(slip_perc_50,50)
# plt.xlabel('Slip (m)')
# plt.grid(True)
# plt.savefig('hist_perc_50_v2.png', transparent = True, bbox_inches='tight', pad_inches=0)

# # percentil 50
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.hist(slip_perc_75,50)
# plt.xlabel('Slip (m)')
# plt.grid(True)
# plt.savefig('hist_perc_75_v2.png', transparent = True, bbox_inches='tight', pad_inches=0)

# # percentil 90
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.hist(slip_perc_90,50)
# plt.xlabel('Slip (m)')
# plt.grid(True)
# plt.savefig('hist_perc_90_v2.png', transparent = True, bbox_inches='tight', pad_inches=0)

# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.hlines([0.5,0.75,0.9],0,130,linestyle='dashed')
# ax.plot(xcdf_falla_completa,ycdf_falla_completa, drawstyle='steps-post')
# ax.set_ylim((0,1))
# ax.set_xlim((0,np.ceil(xcdf_falla_completa.max())))
# plt.xlabel('Slip (m)')
# plt.ylabel('Probability')
# plt.title('ECDF')
# plt.grid(True)
# plt.savefig('ecdf_completo4.png', transparent = True, bbox_inches='tight', pad_inches=0)


# ecdf por segmento
fig = plt.figure(figsize=(9,16))
ax1  = fig.add_subplot(5,3,1)
#ax1.set_aspect(ar)
ax1.plot(xnorte_a_cdf,ynorte_a_cdf, drawstyle='steps-post')

ax2  = fig.add_subplot(5,3,2)
ax2.tick_params(left=False, labelleft=False)
#ax2.set_aspect(ar)
ax2.plot(xnorte_b_cdf,ynorte_b_cdf, drawstyle='steps-post')

ax3  = fig.add_subplot(5,3,3)
ax3.tick_params(left=False, labelleft=False)
#ax3.set_aspect(ar)
ax3.plot(xnorte_c_cdf,ynorte_c_cdf, drawstyle='steps-post')

ax4  = fig.add_subplot(5,3,4)
#ax4.set_aspect(ar)
ax4.plot(xcentronorte_a_cdf,ycentronorte_a_cdf, drawstyle='steps-post')

ax5  = fig.add_subplot(5,3,5)
ax5.tick_params(left=False, labelleft=False)
#ax5.set_aspect(ar)
ax5.plot(xcentronorte_b_cdf,ycentronorte_b_cdf, drawstyle='steps-post')

ax6  = fig.add_subplot(5,3,6)
ax6.tick_params(left=False, labelleft=False)
#ax6.set_aspect(ar)
ax6.plot(xcentronorte_c_cdf,ycentronorte_c_cdf, drawstyle='steps-post')

ax7  = fig.add_subplot(5,3,7)
#ax7.set_aspect(ar)
ax7.plot(xcentro_a_cdf,ycentro_a_cdf, drawstyle='steps-post')
plt.ylabel('Probability')

ax8  = fig.add_subplot(5,3,8)
ax8.tick_params(left=False, labelleft=False)
#ax8.set_aspect(ar)
ax8.plot(xcentro_b_cdf,ycentro_b_cdf, drawstyle='steps-post')

ax9  = fig.add_subplot(5,3,9)
ax9.tick_params(left=False, labelleft=False)
#ax9.set_aspect(ar)
ax9.plot(xcentro_c_cdf,ycentro_c_cdf, drawstyle='steps-post')

ax10 = fig.add_subplot(5,3,10)
#ax10.set_aspect(ar)
ax10.plot(xcentrosur_a_cdf,ycentrosur_a_cdf, drawstyle='steps-post')

ax11 = fig.add_subplot(5,3,11)
ax11.tick_params(left=False, labelleft=False)
#ax11.set_aspect(ar)
ax11.plot(xcentrosur_b_cdf,ycentrosur_b_cdf, drawstyle='steps-post')

ax12 = fig.add_subplot(5,3,12)
ax12.tick_params(left=False, labelleft=False)
#ax12.set_aspect(ar)
ax12.plot(xcentrosur_c_cdf,ycentrosur_c_cdf, drawstyle='steps-post')

ax13 = fig.add_subplot(5,3,13)
#ax13.set_aspect(ar)
ax13.plot(xsur_a_cdf,ysur_a_cdf, drawstyle='steps-post')

ax14 = fig.add_subplot(5,3,14)
ax14.tick_params(left=False, labelleft=False)
#ax14.set_aspect(ar)
ax14.plot(xsur_b_cdf,ysur_b_cdf, drawstyle='steps-post')
plt.xlabel('Slip (m)')

ax15 = fig.add_subplot(5,3,15)
ax15.tick_params(left=False, labelleft=False)
#ax15.set_aspect(ar)
ax15.plot(xsur_c_cdf,ysur_c_cdf, drawstyle='steps-post')

plt.subplots_adjust(hspace=0.3,wspace=0.1)
plt.savefig('ecdf_por_segmentos_fallas3.png', transparent = True, bbox_inches='tight', pad_inches=0)


# histogramas por percentiles
# percentil 50
fig = plt.figure(figsize=(9,16))
ax1  = fig.add_subplot(5,3,1)
ax1.hist(p50_norte_a,50)
ax1.set_xlim((0,40))

ax2  = fig.add_subplot(5,3,2)
ax2.tick_params(left=False, labelleft=False)
ax2.hist(p50_norte_b,50)
ax2.set_xlim((0,40))
plt.title('Slip values at percentile 50',fontsize=18)

ax3  = fig.add_subplot(5,3,3)
ax3.tick_params(left=False, labelleft=False)
ax3.hist(p50_norte_c,50)
ax3.set_xlim((0,40))

ax4  = fig.add_subplot(5,3,4)
ax4.hist(p50_centronorte_a,50)
ax4.set_xlim((0,40))

ax5  = fig.add_subplot(5,3,5)
ax5.tick_params(left=False, labelleft=False)
ax5.hist(p50_centronorte_b,50)
ax5.set_xlim((0,40))

ax6  = fig.add_subplot(5,3,6)
ax6.tick_params(left=False, labelleft=False)
ax6.hist(p50_centronorte_c,50)
ax6.set_xlim((0,40))

ax7  = fig.add_subplot(5,3,7)
ax7.hist(p50_centro_a,50)
ax7.set_xlim((0,40))

ax8  = fig.add_subplot(5,3,8)
ax8.tick_params(left=False, labelleft=False)
ax8.hist(p50_centro_b,50)
ax8.set_xlim((0,40))

ax9  = fig.add_subplot(5,3,9)
ax9.tick_params(left=False, labelleft=False)
ax9.hist(p50_centro_c,50)
ax9.set_xlim((0,40))

ax10 = fig.add_subplot(5,3,10)
ax10.hist(p50_centrosur_a,50)
ax10.set_xlim((0,40))

ax11 = fig.add_subplot(5,3,11)
ax11.tick_params(left=False, labelleft=False)
ax11.hist(p50_centrosur_b,50)
ax11.set_xlim((0,40))

ax12 = fig.add_subplot(5,3,12)
ax12.tick_params(left=False, labelleft=False)
ax12.hist(p50_centrosur_c,50)
ax12.set_xlim((0,40))

ax13 = fig.add_subplot(5,3,13)
ax13.hist(p50_sur_a,50)
ax13.set_xlim((0,40))

ax14 = fig.add_subplot(5,3,14)
ax14.tick_params(left=False, labelleft=False)
ax14.hist(p50_sur_b,50)
ax14.set_xlim((0,40))
plt.xlabel('Slip (m)')

ax15 = fig.add_subplot(5,3,15)
ax15.tick_params(left=False, labelleft=False)
ax15.hist(p50_sur_c,50)
ax15.set_xlim((0,40))
plt.subplots_adjust(hspace=0.3,wspace=0.1)
plt.savefig('p50_por_segmentos_fallas3.png', transparent = True, bbox_inches='tight', pad_inches=0)



# pecentil 75
fig = plt.figure(figsize=(9,16))
ax1  = fig.add_subplot(5,3,1)
ax1.hist(p75_norte_a,50)
ax1.set_xlim((0,40))

ax2  = fig.add_subplot(5,3,2)
ax2.tick_params(left=False, labelleft=False)
ax2.hist(p75_norte_b,50)
ax2.set_xlim((0,40))
plt.title('Slip values at percentile 75',fontsize=18)

ax3  = fig.add_subplot(5,3,3)
ax3.tick_params(left=False, labelleft=False)
ax3.hist(p75_norte_c,50)
ax3.set_xlim((0,40))

ax4  = fig.add_subplot(5,3,4)
ax4.hist(p75_centronorte_a,50)
ax4.set_xlim((0,40))

ax5  = fig.add_subplot(5,3,5)
ax5.tick_params(left=False, labelleft=False)
ax5.hist(p75_centronorte_b,50)
ax5.set_xlim((0,40))

ax6  = fig.add_subplot(5,3,6)
ax6.tick_params(left=False, labelleft=False)
ax6.hist(p75_centronorte_c,50)
ax6.set_xlim((0,40))

ax7  = fig.add_subplot(5,3,7)
ax7.hist(p75_centro_a,50)
ax7.set_xlim((0,40))

ax8  = fig.add_subplot(5,3,8)
ax8.tick_params(left=False, labelleft=False)
ax8.hist(p75_centro_b,50)
ax8.set_xlim((0,40))

ax9  = fig.add_subplot(5,3,9)
ax9.tick_params(left=False, labelleft=False)
ax9.hist(p75_centro_c,50)
ax9.set_xlim((0,40))

ax10 = fig.add_subplot(5,3,10)
ax10.hist(p75_centrosur_a,50)
ax10.set_xlim((0,40))

ax11 = fig.add_subplot(5,3,11)
ax11.tick_params(left=False, labelleft=False)
ax11.hist(p75_centrosur_b,50)
ax11.set_xlim((0,40))

ax12 = fig.add_subplot(5,3,12)
ax12.tick_params(left=False, labelleft=False)
ax12.hist(p75_centrosur_c,50)
ax12.set_xlim((0,40))

ax13 = fig.add_subplot(5,3,13)
ax13.hist(p75_sur_a,50)
ax13.set_xlim((0,40))

ax14 = fig.add_subplot(5,3,14)
ax14.tick_params(left=False, labelleft=False)
ax14.hist(p75_sur_b,50)
ax14.set_xlim((0,40))
plt.xlabel('Slip (m)')

ax15 = fig.add_subplot(5,3,15)
ax15.tick_params(left=False, labelleft=False)
ax15.hist(p75_sur_c,50)
ax15.set_xlim((0,40))

plt.subplots_adjust(hspace=0.3,wspace=0.1)
plt.savefig('p75_por_segmentos_fallas3.png', transparent = True, bbox_inches='tight', pad_inches=0)


# pecentil 90
fig = plt.figure(figsize=(9,16))
ax1  = fig.add_subplot(5,3,1)
ax1.hist(p90_norte_a,50)
ax1.set_xlim((0,40))

ax2  = fig.add_subplot(5,3,2)
ax2.tick_params(left=False, labelleft=False)
ax2.hist(p90_norte_b,50)
ax2.set_xlim((0,40))
plt.title('Slip values at percentile 90',fontsize=18)

ax3  = fig.add_subplot(5,3,3)
ax3.tick_params(left=False, labelleft=False)
ax3.hist(p90_norte_c,50)
ax3.set_xlim((0,40))

ax4  = fig.add_subplot(5,3,4)
ax4.hist(p90_centronorte_a,50)
ax4.set_xlim((0,40))

ax5  = fig.add_subplot(5,3,5)
ax5.tick_params(left=False, labelleft=False)
ax5.hist(p90_centronorte_b,50)
ax5.set_xlim((0,40))

ax6  = fig.add_subplot(5,3,6)
ax6.tick_params(left=False, labelleft=False)
ax6.hist(p90_centronorte_c,50)
ax6.set_xlim((0,40))

ax7  = fig.add_subplot(5,3,7)
ax7.hist(p90_centro_a,50)
ax7.set_xlim((0,40))

ax8  = fig.add_subplot(5,3,8)
ax8.tick_params(left=False, labelleft=False)
ax8.hist(p90_centro_b,50)
ax8.set_xlim((0,40))

ax9  = fig.add_subplot(5,3,9)
ax9.tick_params(left=False, labelleft=False)
ax9.hist(p90_centro_c,50)
ax9.set_xlim((0,40))

ax10 = fig.add_subplot(5,3,10)
ax10.hist(p90_centrosur_a,50)
ax10.set_xlim((0,40))

ax11 = fig.add_subplot(5,3,11)
ax11.tick_params(left=False, labelleft=False)
ax11.hist(p90_centrosur_b,50)
ax11.set_xlim((0,40))

ax12 = fig.add_subplot(5,3,12)
ax12.tick_params(left=False, labelleft=False)
ax12.hist(p90_centrosur_c,50)
ax12.set_xlim((0,40))

ax13 = fig.add_subplot(5,3,13)
ax13.hist(p90_sur_a,50)
ax13.set_xlim((0,40))

ax14 = fig.add_subplot(5,3,14)
ax14.tick_params(left=False, labelleft=False)
ax14.hist(p90_sur_b,50)
ax14.set_xlim((0,40))
plt.xlabel('Slip (m)')

ax15 = fig.add_subplot(5,3,15)
ax15.tick_params(left=False, labelleft=False)
ax15.hist(p90_sur_c,50)
ax15.set_xlim((0,40))

plt.subplots_adjust(hspace=0.3,wspace=0.1)
plt.savefig('p90_por_segmentos_fallas3.png', transparent = True, bbox_inches='tight', pad_inches=0)
