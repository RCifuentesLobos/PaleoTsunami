import numpy as np
import os
import matplotlib.pyplot as plt 
from clawpack.geoclaw import dtopotools

"""
PARAMETROS INICIALES DE DIRECTORIOS Y DATOS
"""
# directorio con funciones
dir_src  = os.getcwd()
# directorio con datos
dir_data = dir_src + "/../data"
# archivo con datos
inv_par = "parametros_inversion.txt"
inv_par = dir_data + "/" + inv_par 

"""
CARGAR DATOS
"""
#Lat. Lon. depth slip rake strike dip
lats, lons, prof, slip, rake, strike, dip = np.loadtxt(inv_par, unpack = True)
slip /= 100 # transformar a metros
nx = 33 # numero sf along strike
ny = 21 # numero sf downdip
Dx = 8000. # tamano sf along strike (metros)
Dy = 1750. # tamano sf down dip (metros)
largo_falla   = nx*Dx
ancho_falla   = ny*Dy 
razon_aspecto = largo_falla/ancho_falla
# cambiar de vector a matriz 
lats   = np.reshape(lats,(nx,ny))
lons   = np.reshape(lons,(nx,ny))
prof   = np.reshape(lats,(nx,ny))
slip   = np.reshape(lats,(nx,ny))
rake   = np.reshape(lats,(nx,ny))
strike = np.reshape(lats,(nx,ny))
dip    = np.reshape(dip,(nx,ny))

"""
CALCULO DEFORMACION
"""
resolucion = 1/30.
tamano_buffer = 2.
verbose = True
# se crea el objeto falla
Falla = dtopotools.Fault() # instancia Falla de la clase dtopotools.Fault()

# parametros auxiliares para creacion de subfallas
n_subfallas = int( np.size( lats ) ) # cantidad total de subfallas
n_subfallas_filas = int( np.shape( lats )[0] ) # numero de filas (latitudes)
n_subfallas_columnas = int( np.shape( lats )[1] ) # numero de columnas (longitudes)
ancho_falla = largo_falla / razon_aspecto # ancho total de la falla
largo_subfalla = largo_falla / n_subfallas_filas # largo de cada subfalla
ancho_subfalla = ancho_falla / n_subfallas_columnas # ancho de cada subfalla

# creacion de subfallas
Falla.subfaults = [] # inicializacion lista con subfallas, se anadira a esta lista los atributos de cada subfalla
for subfalla in range(int(n_subfallas)):
    SubFalla = dtopotools.SubFault() # iniciacion de instancia SubFalla de la clase dtopotools.SubFault. A este objeto se le anadiran los atributos que siguen para crear la falla "Falla"
    SubFalla.latitude = np.reshape( lats, ( np.size( lats ),) )[subfalla] # latitud de cada subfalla
    SubFalla.longitude = np.reshape( lons,( np.size( lons ),))[subfalla] # longitud de cada subfalla
    SubFalla.strike = np.reshape( strike, ( np.size( strike ),))[subfalla] # strike de cada subfalla
    SubFalla.rake = np.reshape( rake,( np.size( rake ),))[subfalla] # rake de cada subfalla
    SubFalla.depth = np.reshape( prof, ( np.size( prof ),))[subfalla] # profundidad de cada subfalla en metros
    SubFalla.dip = np.reshape( dip,( np.size( dip ),))[subfalla] # dip de cada subfalla
    SubFalla.slip = np.reshape( slip, ( np.size( slip ),))[subfalla] # slip de cada subfalla 
    SubFalla.length = (np.ones( np.size( slip )) * largo_subfalla)[subfalla] # largo de cada subfalla en metros
    SubFalla.width = (np.ones( np.size( slip )) * ancho_subfalla)[subfalla] # ancho de cada subfalla en metros
    SubFalla.coordinate_specification = 'centroid'
    Falla.subfaults = np.append(Falla.subfaults, SubFalla)

# se crea la topografia  
x,y = Falla.create_dtopo_xy( dx = resolucion, buffer_size = tamano_buffer ) 
# se calcula la deformacion
dtopo = Falla.create_dtopography(x,y,times=[1.], verbose = verbose ) # deformacion

"""
GUARDAR XYZ
"""
# extraer datos
X = dtopo.X
Y = dtopo.Y
Z = dtopo.dZ

# crear xyz
data = np.stack([X.ravel(), Y.ravel(), Z.ravel()],axis = 1)

# guardar xyz
nombre_salida_def = "deformacion_2018.xyz"
np.savetxt(nombre_salida_def, data, fmt = '%3.6f')