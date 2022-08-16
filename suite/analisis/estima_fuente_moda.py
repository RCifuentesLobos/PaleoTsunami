"""
CALCULA LA MODA DE LOS MODELOS QUE PASAN LAS RESTRICCIONES Y ESCALA LA MAGNITUD DE MOMENTO A LA MAGNITUD MAS PROBABLE 
SEGUN LAS RAMAS DEL AL
"""


import os
import glob
import numpy as np
from scipy.stats import mode
import modokada as mo 
import modfallas as mf 
import csv
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import gc 
from scipy.interpolate import interp2d

gc.collect()

"""
MAGNITUD DE MOMENTO DE ARBOL
"""
Mw_deseado = 9.0

"""
PARAMETROS DE DIRECTORIO
"""
# directorio actual
dir_actual = os.getcwd()
# directorio con modelos restringidos
ruta_slip="../fallas2/fallas2/modelos_restringidos/modelos_restringidos_meridionalmente1/modelos_restringidos_meridionalmente2/modelos_restringidos_meridionalmente3/modelos_restringidos_meridionalmente4/modelos_restringidos_magdatos"
#ruta_slip  = "../ctl_tsunami/modelacion_orden_ctdad_datos/castrodalcahue/modelos_restringidos" 

"""
CARGAR FOSA Y LECTURA DE ARCHIVOS DE SLAB
"""

# ruta del archivo de la fosa
ruta_fosa = "../Slab/"
# archivo fosa ( primera columna: longitudes, segunda columna: latitudes)
arc_fosa  = ruta_fosa + "SAM3.txt"
# carga de fosa usando funcion del modulo modfallas
lonfosa, latfosa  = mf.carga_fosa(arc_fosa)

# archivo de profundidad
proffile   = ruta_fosa + "sam_slab2_dep_02.23.18.xyz" # nombre del archivo de prof
slabprof   = np.genfromtxt(proffile, delimiter = ",") # se lee el archivo a un array
# archivo de dip
dipfile    = ruta_fosa + "sam_slab2_dip_02.23.18.xyz" # nombre del archivo de dip
slabdip    = np.genfromtxt(dipfile, delimiter = ",") # se lee el archivo a un array
# archivo de strike
strfile    = ruta_fosa + "sam_slab2_str_02.23.18.xyz"
slabstrike = np.genfromtxt(strfile, delimiter = ",") # se lee el archivo a un array
# archivo de rakes
rakefile   = ruta_fosa + "sam_rake.xyz"
slabrake   = np.genfromtxt(rakefile, delimiter = ",")
print("datos de slab cargados")


"""
PREACONDICIONAMIENTO DE DATOS PARA CALCULOS POSTERIORES
"""

# las longitudes estan en formato 0 - 360, se cambian a -180 - 180
slabprof[:,0]   = slabprof[:,0]   - 360
slabdip[:,0]    = slabdip[:,0]    - 360
slabstrike[:,0] = slabstrike[:,0] - 360

# longitudes y latitudes del modelo
lonmod = slabprof[:,0]
latmod = slabprof[:,1]
# longitudes y latitudes unicas del modelo
lonunimod = np.unique(lonmod) # x
latunimod = np.unique(latmod) # y
# se grillan los arrays
lonmodgrid, latmodgrid = np.meshgrid(lonunimod, np.flip(latunimod)) # X, Y datos grillados para graficar modelo completo

# profundidades, dips y strikes del modelo
profmod   = slabprof[:,2]*-1000. # metros positivos hacia abajo
dipmod    = slabdip[:,2]
strikemod = slabstrike[:,2]
# se grillan los datos
profmod   = np.reshape(profmod,np.shape(lonmodgrid))
dipmod    = np.reshape(dipmod,np.shape(lonmodgrid))
strikemod = np.reshape(strikemod,np.shape(lonmodgrid))
# cambiar nan por 0
idx_nan_prof_mod   = np.isnan(profmod)
idx_nan_dip_mod    = np.isnan(dipmod)
idx_nan_strike_mod = np.isnan(strikemod)
profmod[idx_nan_prof_mod]     = 0 # profundidad grillada con 0 en lugar de nan
dipmod[idx_nan_dip_mod]       = 0 # dip grillado con 0 en lugar de nan
strikemod[idx_nan_strike_mod] = 0 # strike grillado con 0 en lugar de nan
print("preacondicionamiento terminado")


"""
IR A DIRECTORIO DE TRABAJO
"""
os.chdir(ruta_slip)

"""
CARGAR LISTAS
"""
# lista con todos los archivos npz sobre los que se iterara
lista_npz  = glob.glob("*.npz")       # lista con arrays de slip y coordenadas
lista_npz.sort(key=os.path.getctime)  
print("lista de npz cargada")


"""
LOOP PARA CALCULAR MODA
"""


# inicializar matriz de calculo de promedio
ini_data        = np.load(lista_npz[0])
array_prom_slip = np.zeros(ini_data["Slip"].shape)
# inicializar matriz de calculo de moda
array_slips = np.zeros( ini_data["Slip"].shape + (len(lista_npz),) )

# coordenadas
lons = ini_data["array_lons"]
lats = ini_data["array_lats"]
# calculo largo de falla
largo_falla = mf.dist_sf_alt(-72.,-72.,lats.max(), lats.min())

"""
INTERPOLACION DE PARAMETROS GEOMETRICOS
"""
# se crea un interpolador: se debe limitar el area total del modelo slab 2.0 al area de interes mas un buffer para ahorrar costos computacionales
# se corta el modelo completo al area de interes
latnorte = lats.max() + 1.
latsur   = lats.min() - 1.
loneste  = lons.max() + 1. 
lonoeste = lons.min() - 1.

idx_mascara_lons = np.argwhere( (lonmodgrid > lonoeste) & (lonmodgrid < loneste) )
idx_mascara_lats = np.argwhere( (latmodgrid > latsur) & ( latmodgrid < latnorte) )


def coincidencias_filas(A,B):
    coincidencias  =  [i for i in range(B.shape[0]) if np.any(np.all(A==B[i],axis=1))]
    if len(coincidencias)==0:
        return B[coincidencias]
    return np.unique(B[coincidencias],axis=0)

mascara = coincidencias_filas(idx_mascara_lons, idx_mascara_lats)
# se cuenta la cantidad de columnas y filas con las que cuenta el rectangulo recortado
primer_elemento_mascara = mascara[0,0] # se cuenta cuants veces se repite este elemento (que corresponde al indice de la primera fila del rectangulo de interes) para saber cuantas columnas tiene el rectangulo
n_columnas_area_interes = np.shape(mascara[mascara[:,0]==primer_elemento_mascara,:])[0]
n_filas_area_interes    = np.shape(mascara)[0]/n_columnas_area_interes
print("mascara creada")

# dimensiones de la mascara
dim_mascara          = np.shape(mascara)
dim_mascara_filas    = dim_mascara[0]
dim_mascara_columnas = dim_mascara[1]

# longitud cortada al area de interes
lonmodgrid_cortado = np.ones((dim_mascara_filas,1))
for i in range(dim_mascara_filas):
    lonmodgrid_cortado[i] = lonmodgrid[mascara[i,0],mascara[i,1]]
print("longitud cortada")
# latitud cortadad al area de interes
latmodgrid_cortado = np.ones((dim_mascara_filas,1))
for j in range(dim_mascara_filas):
    latmodgrid_cortado[j] = latmodgrid[mascara[j,0],mascara[j,1]]
print("latitud cortada")

# profundidad del modelo cortado al area de interes
profmod_cortado = np.ones((dim_mascara_filas,1))
for h in range(dim_mascara_filas):
    profmod_cortado[h] = profmod[mascara[h,0],mascara[h,1]]

# se amolda a las dimensiones correctas
profmod_cortado = np.reshape(profmod_cortado,(n_filas_area_interes, n_columnas_area_interes))

# dip del modelo cortado al area de interes
dipmod_cortado = np.ones((dim_mascara_filas,1))
for d in range(dim_mascara_filas):
    dipmod_cortado[d] = dipmod[mascara[d,0],mascara[d,1]]

# se amolda a las dimensiones correctas
dipmod_cortado = np.reshape(dipmod_cortado,(n_filas_area_interes, n_columnas_area_interes))

# strike del modelo cortado al area de interes
strikemod_cortado = np.ones((dim_mascara_filas,1))
for s in range(dim_mascara_filas):
    strikemod_cortado[s] = strikemod[mascara[s,0],mascara[s,1]]

# se amolda a las dimensiones correctas
strikemod_cortado = np.reshape(strikemod_cortado, (n_filas_area_interes, n_columnas_area_interes))

# grilla del area de interes
lonmodgrid_cortado_area = np.reshape(lonmodgrid_cortado, (n_filas_area_interes, n_columnas_area_interes))
latmodgrid_cortado_area = np.reshape(latmodgrid_cortado, (n_filas_area_interes, n_columnas_area_interes))
print("slab cortado a area de interes")

# interpolador de profundidad
interpolador_prof   = interp2d(lonmodgrid_cortado_area[0,:], latmodgrid_cortado_area[:,0], profmod_cortado, kind='cubic')

# interpolador de dip
interpolador_dip    = interp2d(lonmodgrid_cortado_area[0,:], latmodgrid_cortado_area[:,0], dipmod_cortado, kind='cubic')

# interpolador de strike
interpolador_strike = interp2d(lonmodgrid_cortado_area[0,:], latmodgrid_cortado_area[:,0], strikemod_cortado, kind='cubic')

# interpolador de rake
interpolador_rake   = interp2d(slabrake[:,0], slabrake[:,1], slabrake[:,2], kind = 'cubic')
print("interpoladores creados")

###################
# interpolaciones #
###################

print("comenzando interpolacion")
# profundidad
prof_subfallas_int  = np.ones(np.shape(lons))
for i in range(np.shape(lons)[0]):
    for j in range(np.shape(lons)[1]):
        prof_subfallas_int[i,j]   = interpolador_prof(lons[i,j], lats[i,j])
prof_subfallas_int = np.abs(prof_subfallas_int)
# dip
dip_subfallas_int   = np.ones(np.shape(lons))
for i in range(np.shape(lons)[0]):
    for j in range(np.shape(lons)[1]):
        dip_subfallas_int[i,j]    = interpolador_dip(lons[i,j], lats[i,j])

# strike
strike_subfallas_int = np.ones(np.shape(lons))
for i in range(np.shape(lons)[0]):
    for j in range(np.shape(lons)[1]):
        strike_subfallas_int[i,j] = interpolador_strike(lons[i,j], lats[i,j])

# rake
rake_subfallas_int   = np.ones(np.shape(lons))
for i in range(np.shape(lons)[0]):
    for j in range(np.shape(lons)[1]):
        rake_subfallas_int[i,j] = interpolador_rake(lons[i,j], lats[i,j])
print("interpolaciones terminadas")


"""
CALCULO DE MODA
"""
# creacion de array con slips
for i in range(len(lista_npz)):
    data = np.load(lista_npz[i])
    slip = data["Slip"]
    array_slips[:,:,i] = slip

# calculo de moda
moda_slip = np.squeeze(mode(array_slips, axis=2)[0]) 
print("Moda calculada")


"""
CALCULO MAGNITUD DE MOMENTO
"""
Mw = mo.calcula_Mw(lons, lats, 7/2, strike_subfallas_int,dip_subfallas_int,prof_subfallas_int, rake_subfallas_int, moda_slip, largo_falla)
print(Mw)



"""
ESCALAR MAGNITUD DE MOMENTO
"""
Slip_final = mf.escalar_magnitud_momento(Mw_deseado, moda_slip, prof_subfallas_int, lons, lats) 


"""
CALCULO DEFORMACION
"""
print("Calculando deformacion vertical")
deformacion_escalada = mo.okada_solucion(lons, lats, 7/2, strike_subfallas_int,dip_subfallas_int,prof_subfallas_int, rake_subfallas_int, Slip_final, largo_falla, verbose=True)

"""
GUARDAR DEFORMACION
"""
# como falla .tt3
nombre_archivo_def_salida = "def_vertical_estimada_rest_magdatos.tt3"
mo.guardar_okada(deformacion_escalada, nombre_archivo_def_salida)
print("Deformacion vertical guardada en directorio %s como %s") %(dir_actual, nombre_archivo_def_salida)

# como csv

lonsdef = deformacion_escalada.X
latsdef = deformacion_escalada.Y 
deltaZ  = np.squeeze(deformacion_escalada.dZ)
data = np.stack([lonsdef.ravel(), latsdef.ravel(), deltaZ.ravel()],axis = 1)
nombre_archivo_def_salida_csv = "def_vertical_estimada_rest_magdatos.csv" 
with open(nombre_archivo_def_salida_csv,"w") as f:
    writer = csv.writer(f)
    writer.writerows(data)



"""
FIGURA MODA
"""

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
csmoda = m.pcolormesh(mlons, mlats, Slip_final)
cbar = m.colorbar(csmoda,location='bottom',pad="5%")
cbar.set_label('m')
# anexos
m.plot(mfosalons, mfosalats, marker=None, color='k')
m.drawcoastlines()
m.drawcountries(linewidth=0.25)
m.drawmeridians(np.arange(-180,180,2),labels=[1,1,0,1])
m.drawparallels(np.arange(-50,-30,2),labels=[1,1,0,1])
plt.title('Source')
plt.show()
plt.savefig('fuente_estimada_moda_rest_magdatos.png', transparent = True, bbox_inches='tight', pad_inches=0)


"""
VOLVER A DIRECTORIO DE ORIGEN
"""
os.chdir(dir_actual)