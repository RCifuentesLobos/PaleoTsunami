# maneja los archivos de deformacion para modelar tsunami
import Tkinter,tkFileDialog
from tkinter import *
from tkinter import ttk
import subprocess
import os
import glob
import shutil 
import sys
import json
import numpy as np
import pandas as pd
import modokada as mo 
import modfallas as mf 
import modrestricciones as mr
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from scipy.interpolate import RegularGridInterpolator, interp1d, interp2d ,griddata, Rbf
from geographiclib.geodesic import Geodesic
from formato_comcotctl2 import crea_comcotctl
import gc 

gc.collect()



# ruta datos de deformacion ya restringidos convertidos a csv


"""
INFO DE DIRECTORIOS
"""
ruta_deformaciones = "/media/rodrigo/Seagate Expansion Drive/tesis/modelaciones_norte/Resolucion/fallas2/modelos_restringidos/restriccion_fuerte/csv_files"
dir_destino        = "/media/rodrigo/Seagate Expansion Drive/tesis/modelaciones_norte/Resolucion/ctl_tsunami"
dir_comcot         = "/media/rodrigo/Seagate Expansion Drive/tesis/modelaciones_norte/Resolucion/ctl_tsunami"
dir_modelacion     = "/media/rodrigo/Seagate Expansion Drive/tesis/modelaciones_norte/Resolucion/tsunami"
dir_grillas        = "/media/rodrigo/Seagate Expansion Drive/tesis/modelaciones_norte/Resolucion/grillas_comcot"
dir_actual         = os.getcwd()     # ruta al directorio principal 


"""
CARGAR LISTAS
"""
os.chdir(ruta_deformaciones)  # se cambia al directorio con informacion de deformaciones
# lista con todos los archivos npz sobre los que se iterara
lista_def  = glob.glob("deformacion*.csv") # lista con arrays de deformacion y coordenadas
lista_def.sort(key=os.path.getctime)       # lista ordenada
lista_slip = glob.glob("slip*.csv")        # lista con arrays de slip y coordenadasd
lista_slip.sort(key=os.path.getctime)      # lista ordenada

print("%s archivos de fallas leidos") %(len(lista_def))

"""
SELECCION DE GRILLAS
"""
# seleccionar grillas a graficar
# funcion para seleccionar grillas
def seleccion_grillas():
    os.chdir(dir_grillas)
    root = Tkinter.Tk()
    grillas_seleccion = tkFileDialog.askopenfilenames(parent=root,multiple=True,title='Elija las grillas')
    lista_grillas  = list(grillas_seleccion) # lista con las grillas seleccionadas y sus rutas
    largo_ruta_grillas = len(dir_grillas) + 1 # largo de string de caracteres que debe ser quitado de la ruta completa para obtener solo el nombre, el +1 se agrega para tomar en cuenta el / faltante en la definicion de dir grillas
    lista_nombre_grillas = []
    # obtener solo el nombre de los archivos de grilla, sin ruta
    for grilla in lista_grillas:
        nombre_grilla = grilla[largo_ruta_grillas:].strip()
        lista_nombre_grillas.append(nombre_grilla)
    root.destroy()
    # se explicita que grillas fueron seleccionadas
    print("%s grillas seleccionadas ") %(len(lista_nombre_grillas))
    print("")
    print(lista_nombre_grillas)
    return lista_nombre_grillas

print("Seleccionar grillas")
# se llama la funcion
lista_nombre_grillas = seleccion_grillas()
# se confirma que la seleccion este correcta
decision_grillas = raw_input("Confirmar seleccion? [s/n]: ")
# si no esta correcta, se vuelve a preguntar
while decision_grillas == "n":
    seleccion_grillas()
    decision_grillas = raw_input("Confirmar seleccion? [s/n]: ")
if decision_grillas == "s":
    print("%s grillas correctamente seleccionadas: ") %(len(lista_nombre_grillas))
    print("")
    print(lista_nombre_grillas)

##
# se muestra graficamente la disposicion de las grillas utilizadas
##

# funcion para encontrar los limites de las grillas seleccionadas 
def limites_grillas(dir_grillas, lista_nombre_grillas):
    """
    ENTRADAS:
    dir_grillas: ruta a directorio con las grillas originales
    lista_nombre_grillas: lista con grillas seleccionadas
    """
    # busca los limites de las grillas elegidas ara ser graficadas posteriormente
    # ruta de las grillas para cargarlas y graficarlas
    ruta_grillas = []
    for grilla in lista_nombre_grillas:
        ruta = dir_grillas+"/"+grilla
        ruta_grillas.append(ruta)
    # cantidad de grillas seleccionadas
    n_grillas = len(ruta_grillas)

    # cargar grillas y seleccionar los limites, estos se guardan en un array de 2x2xn_grillas array_limites
    array_limites = np.ones((2,2,n_grillas)) # inicializacion array para limites
    c = 0 # contador auxiliar
    for grilla in ruta_grillas:
        x,y = np.loadtxt(grilla,usecols=(0,1), unpack=True)
        xmin = x.min()
        if xmin > 0:
            x -= 360.
        lonmin = x.min() # llcrnrlon
        array_limites[0,0,c] = lonmin
        lonmax = x.max() # urcrnrlon
        array_limites[0,1,c] = lonmax
        latmin = y.min() # llcrnrlat
        array_limites[1,0,c] = latmin
        latmax = y.max() # urcrnrlat
        array_limites[1,1,c] = latmax
        c += 1
    return array_limites


# funcion para calcular resolucion de grillas
def resolucion_grillas(dir_grillas, lista_nombre_grillas):
    """
    ENTRADAS:
    dir_grillas: ruta a directorio con las grillas originales
    lista_nombre_grillas: lista con grillas seleccionadas
    """
    # busca la resolucion de las grillas para anidamiento
    # ruta de las grillas para cargarlas y calcular resolucion
    ruta_grillas = []
    for grilla in lista_nombre_grillas:
        ruta = dir_grillas+"/"+grilla
        ruta_grillas.append(ruta)
    # cantidad de grillas seleccionadas
    n_grillas = len(ruta_grillas)

    # se cargan las grillas, se calcula la resolucion y se guarda en el array array_resolucion
    array_resolucion = np.ones((n_grillas)) # inicializacion array para guardar resoluciones
    c = 0 # contador auxiliar
    for grillas in ruta_grillas:
        x = np.loadtxt(grillas,usecols=(0), unpack=True)
        dif = round((x[1]-x[0])*60,3)
        array_resolucion[c] = dif
        c += 1
    
    return array_resolucion


# funcion para visualizar las grillas seleccionadas
def grafica_mapa_grillas(dir_grillas, lista_nombre_grillas,flag_res = True):
    # ruta de las grillas para cargarlas y graficarlas
    ruta_grillas = []
    for grilla in lista_nombre_grillas:
        ruta = dir_grillas+"/"+grilla
        ruta_grillas.append(ruta)
    # cantidad de grillas seleccionadas
    n_grillas = len(ruta_grillas)

    # mapa base
    fig = plt.figure()
    ax  = fig.add_subplot(111)
    map = Basemap(llcrnrlon=-84,llcrnrlat=-55,urcrnrlon=-66.,urcrnrlat=-17.,
             resolution='l', projection='merc')
    map.drawmapboundary(fill_color='#A6CAE0')
    map.fillcontinents(color='#e6b800',lake_color='#A6CAE0')
    map.drawparallels(np.arange(-50.,-15.,10.))
    map.drawmeridians(np.arange(-80.,-66.,4.))
    map.drawcountries(color="white")
    map.drawcoastlines()

    # graficar rectangulos con los limites de las grillas
    array_limites    = limites_grillas(dir_grillas, lista_nombre_grillas)
    # funcion para graficar un rectangulo con los limites de la grilla
    def dibuja_rectangulo_grilla(lons, lats, map, num_grilla):
        """
        ENTRADAS:
        lons: longitudes de las esquinas de las grillas [izq izq der der]
        lats: latitudes de las esquinas de las grillas [inf sup sup inf]
        map: instancia del mapa de basemap
        num_grilla: numero identificacion grilla a graficar
        """
        # cambiar esquinas a coordenadas del mapa
        x, y = map(lons,lats)
        xy   = zip(x,y)
        rectangulo = Polygon(xy , facecolor = 'blue', alpha = 0.4, edgecolor = 'k', linewidth = 2 )
        plt.gca().add_patch(rectangulo)
        # cambiar lon y lat de esquina superior derecha a coordenadas del mapa para anotar el id de la grilla
        xid, yid = map(lons[-1], lats[1])
        id_str   = str(num_grilla)
        plt.annotate(id_str, xy=(xid,yid), weight = 'bold', xycoords='data', xytext=(xid,yid), textcoords='data')

    # anotaciones con las resoluciones de las grillas
    # explicitar resolucion de grillas
    array_resolucion = resolucion_grillas(dir_grillas, lista_nombre_grillas)
    # funcion para anotar las resoluciones de las grillas
    if flag_res:
        def anota_resoluciones(map, num_grilla, array_resolucion):
            x, y = 1.2, 0.9-(num_grilla-1)*0.05
            resolucion = str(num_grilla) + ": " + str(array_resolucion[num_grilla-1]) + "'"
            plt.annotate(resolucion, xy=(x,y), weight = 'bold', xycoords='axes fraction', xytext=(x,y), textcoords='axes fraction')
            xtitle, ytitle = 1.2, 0.95
            plt.annotate("Res. grillas", xy=(xtitle,ytitle), weight = 'bold', xycoords='axes fraction', xytext=(xtitle,ytitle), textcoords='axes fraction')

    # grafica de rectangulos de limites de grillas
    # contador auxiliar para numero de 
    c_id = 1
    for i in range(n_grillas):
        lons = [array_limites[0,0,i], array_limites[0,0,i], array_limites[0,1,i], array_limites[0,1,i] ]
        lats = [array_limites[1,0,i], array_limites[1,1,i], array_limites[1,1,i], array_limites[1,0,i] ]
        dibuja_rectangulo_grilla(lons, lats, map, c_id)
        anota_resoluciones( map, c_id, array_resolucion)
        c_id += 1
    
    plt.show()

# se grafica las grillas seleccionadas
print("graficando...")
# llamado a funcion de grafica de grillas
grafica_mapa_grillas(dir_grillas, lista_nombre_grillas)

# se pide reconfirmacion de seleccion de grillas
decision_grillas2 = raw_input("Confirmar seleccion? [s/n]: ")
# si no esta correcta, se vuelve a preguntar
while decision_grillas2 == "n":
    seleccion_grillas()
    decision_grillas2 = raw_input("Confirmar seleccion? [s/n]: ")
if decision_grillas2 == "s":
    print("%s grillas correctamente seleccionadas: ") %(len(lista_nombre_grillas))
    print("Archivos:")
    print(lista_nombre_grillas)

"""
CREACION DE TS_LOCATION.DAT
"""
# funcion para elegir ubicaciones de mareogramas
def crea_tslocations_mapa(dir_grillas, lista_nombre_grillas):
    """
    ENTRADAS:
    dir_grillas: ruta a directorio con las grillas originales
    lista_nombre_grillas: lista con grillas seleccionadas
    """

    main = Tk()
    main.title("Seleccionar grillas")
    main.geometry("300x400")
    frame = ttk.Frame(main, padding=(3, 3, 12, 12))
    frame.grid(column=0, row=0, sticky=(N, S, E, W))

    valores = StringVar()
    valores.set(lista_nombre_grillas)

    lstbox = Listbox(frame, listvariable=valores, selectmode=MULTIPLE, width=35, height=30)
    lstbox.grid(column=0, row=0, columnspan=2)

    def seleccionar():
        lista_seleccionada = list()
        lista_seleccionada = [lstbox.get(i) for i in lstbox.curselection()]
        seleccionar.seleccion = lista_seleccionada
        main.destroy()

    btn = ttk.Button(frame, text="Seleccionar", command=seleccionar)
    btn.grid(column=1, row=1)

    main.mainloop()

    # numero de grillas seleccionadas
    n_seleccion = len(seleccionar.seleccion)
    # lista seleccion
    lista_grillas_seleccionadas = []
    for i in range(n_seleccion):
        lista_grillas_seleccionadas.append(seleccionar.seleccion[i][:].split("'")[1])

    print(lista_grillas_seleccionadas)
    # permite al usuario ingresar las ubicaciones de los mareogramas virtuales ya sea manualmente o a traves de una interfaz grafica, verifica que esten dentro de al menos una grilla

    # se completa la ruta de las grillas
    ruta_grillas = []
    for grilla in lista_grillas_seleccionadas:
        ruta = dir_grillas+"/"+grilla
        ruta_grillas.append(ruta)

    # se busca los limites de las grillas para seleccionar aquellas donde se quiera poner un mareografo
    array_limites = limites_grillas(dir_grillas, lista_grillas_seleccionadas)

    print("graficando...")
    # funcion para buscar los puntos donde se hace click 
    def onclick(event):
        global ix, iy
        global coords
        ix, iy = event.xdata, event.ydata
        #print 'x = %d, y = %d'%(ix, iy)
        coords.append((ix, iy))
        return coords

    # inicializacion de listas con longitud y latitud de las ubicaciones seleccionadas
    lonts_aux = []
    latts_aux = []
    lonts     = []
    latts     = []
    n_clicks  = 0
    # se grafica cada grilla seleccionada
    for i in range(n_seleccion):
        # mapa de grilla
        fig = plt.figure()
        ax  = fig.add_subplot(111)
        map = Basemap(llcrnrlon=array_limites[0,0,i], llcrnrlat=array_limites[1,0,i],
                        urcrnrlon=array_limites[0,1,i],urcrnrlat=array_limites[1,1,i],
                        resolution='h', projection='merc')
        map.drawmapboundary(fill_color='#A6CAE0')
        map.fillcontinents(color='#e6b800',lake_color='#A6CAE0')
        map.drawcountries(color="white")
        map.drawcoastlines()
        # titulo
        x, y = 0.3, 1.05
        titulo_grilla = lista_grillas_seleccionadas[i].split(".")[0]
        plt.annotate(titulo_grilla, xy=(x,y), weight = 'bold', 
            xycoords='axes fraction', xytext=(x,y), textcoords='axes fraction')
        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show()
        for i in range(n_clicks,len(coords)):
            lonts_aux.append( map(coords[i][0], coords[i][1], inverse = True)[0])
            latts_aux.append( map(coords[i][0], coords[i][1], inverse = True)[1])
        lonts.append(lonts_aux)
        latts.append(latts_aux)
        lonts_aux, latts_aux = [], []
        n_clicks = len(coords) # cantidad de ubicaciones seleccionadas
        fig.canvas.mpl_disconnect(cid)
    return lonts, latts, lista_grillas_seleccionadas

# guardar ts_locations a partir de salidas de crea_tslocations_mapa
def guardar_tslocations(lonts, latts, dir_destino, dir_grillas ,lista_grillas_seleccionadas, flag_mapa = 0):
    """
    ENTRADAS
    lonts: longitudes de los mareografos
    latts: latitudes de los mareografos
    dir_destino: directorio donde se guardara el archivo ts
    dir_grillas: directorio donde se guardan las grillas
    lista_grillas_seleccionadas: lista con los nombres de las grillas que fueron seleccionadas para incluir mareografos
    flag_mapa: switch para graficar [1] o no [0], por defecto no se grafica
    """
    # funcion que grafica la ubicacion de los mareografos y guarda las ubicaciones en un archivo
    # se crea las rutas de las grillas

    # se grafica las posiciones de ser deseado
    if flag_mapa:
        ruta_grillas = []
        for grilla in lista_grillas_seleccionadas:
            ruta = dir_grillas+"/"+grilla
            ruta_grillas.append(ruta)
        # cantidad de grillas seleccionadas
        n_grillas = len(ruta_grillas)

        array_limites = limites_grillas(dir_grillas, lista_grillas_seleccionadas)
        # se grafica cada una de las grillas con las ubicaciones seleccionadas
        for i in range(n_grillas):
            fig = plt.figure()
            ax  = fig.add_subplot(111)
            map = Basemap(llcrnrlon=array_limites[0,0,i], llcrnrlat=array_limites[1,0,i],
                            urcrnrlon=array_limites[0,1,i],urcrnrlat=array_limites[1,1,i],
                            resolution='h', projection='merc')
            map.drawmapboundary(fill_color='#A6CAE0')
            map.fillcontinents(color='#e6b800',lake_color='#A6CAE0')
            map.drawcountries(color="white")
            map.drawcoastlines()
            # titulo
            x, y = 0.3, 1.05
            titulo_grilla = lista_grillas_seleccionadas[i].split(".")[0]
            plt.annotate(titulo_grilla, xy=(x,y), weight = 'bold', 
                xycoords='axes fraction', xytext=(x,y), textcoords='axes fraction')
            xi, yi = [], []
            for j in range(len(lonts[i])):
                xi.append(map(lonts[i][j], latts[i][j])[0])
                yi.append(map(lonts[i][j], latts[i][j])[1])
                map.plot(xi[j], yi[j], marker = 'v', color = 'r')
            plt.show()

    # se guarda el archivo
    ts = open("ts_location.dat","a")
    for i in range(len(lonts)):
        for j in range(len(lonts[i])):
            ts.write(str(lonts[i][j]) + " " + str(latts[i][j]) + "\n")
    ts.close()


    

# funcion para elegir archivo ts_locations existe
def buscar_ts_locations():
    root = Tkinter.Tk()
    # archivo ts_location con ruta
    ts_seleccion = tkFileDialog.askopenfilenames(parent=root,title='Escoja archivo ts_location.dat'
                    ,filetypes=(("archivos dat","*.dat"),("todos los archivos","*.*")))
    root.destroy()        
    return ts_seleccion
    
# elegir si se incluye archivo ts
coords = []
decision_ts = raw_input("Desea agregar ts? [s/n] ")
if decision_ts == "s":
    flag_ts = True
    decision_ts2 = raw_input("Seleccionar archivo ts_location.dat existente [1] o elegir ubicaciones en el mapa [2]: ")
    if decision_ts2 == "1":
        buscar_ts_locations()
    elif decision_ts2 == "2":
        lonts, latts, lista_grillas_seleccionadas = crea_tslocations_mapa(dir_grillas, lista_nombre_grillas)
        decision_visualizacion_ts = raw_input("Visualizar ubicaciones de mareografos? [s/n] ")
        if decision_visualizacion_ts == "s":
            flag_ts = 1
        else:
            flag_ts = 0
        guardar_tslocations(lonts, latts, dir_destino, dir_grillas, lista_grillas_seleccionadas, flag_mapa = flag_ts)
    decision_ts3 = raw_input("Desea guardar ts [1] o ts y Zmax [2]? ")
    if decision_ts3 == "1":
        salidas_gral = 1
    elif decision_ts3 == "2":
        salidas_gral = 2
    shutil.copy("ts_location.dat",dir_destino)
    print("ts_locations.dat copiado a directorio de destino")
    



"""
CREACION ARCHIVOS DE CONTROL 
"""
print("creando archivos de control de COMCOT y archivos de entrada de def.")
for arc_def in lista_def:
    if flag_ts:
        crea_comcotctl(arc_def, ruta_deformaciones, lista_nombre_grillas, salidas_gral=salidas_gral)
    else:
        crea_comcotctl(arc_def, ruta_deformaciones, lista_nombre_grillas)
    # preparacion archivo de deformacion de entrada
    def_if = str(arc_def.split("_")[1].split(".")[0]) # formato de nombre es deformacion_n.csv, se guarda solo el valor de n como identificador para crear archivo comcot_n.ctl
    # nombre del archivo ctl que se guardara para cada archivo de deformacion
    nombre_archivo_ctl = "comcot_"+def_if+".ctl"
    nombre_archivo_xyz = arc_def.replace("csv","xyz")
    shutil.move(nombre_archivo_ctl, dir_destino)
    shutil.move(nombre_archivo_xyz, dir_destino)
    print("modelo numero %s listo") %(def_if)

print("creacion de archivos de control lista")
print("copiando grillas seleccionadas")
for grilla in lista_nombre_grillas:
    shutil.copy(grilla, dir_destino)
print("grillas copiadas")



"""
MODELACION
"""
# se cambia al directorio donde se realizara la modelacion
print("cambiando a directorio de modelaciones")
os.chdir(dir_comcot)
# se hace un listado con los archivos ctl
lista_ctl  = glob.glob("comcot_*.ctl") # lista con arrays de deformacion y coordenadas
lista_ctl.sort(key=os.path.getctime)       # lista ordenada
# se decide si la modelacion se realizara en subdirectorios dentro del directorio con archivos ctl o no
decision_dir_modelacion = raw_input("Guardar resultados en directorio ctl [1] u en directorio definido en inicio [2]? ")
if decision_dir_modelacion == "1":
    dir_modelacion = dir_comcot
else:
    dir_modelacion = dir_modelacion
# se comienza creando un directorio por cada modelacion, para no mezclar ni sobreescribir resultados
print("comenzando creacion de directorios de modelacion")
for ctl in lista_ctl:
    # se crea un directorio por cada elemento
    dir_ctl = ctl.split(".")[0] # nombre del archivo ctl (sin .ctl)
    nid_ctl = ctl.split("_")[1].split(".")[0] # numero identificador del archivo ctl
    os.mkdir(dir_ctl) # se crea el directorio donde se realizara la modelacion
    # se copian los archivos necesarios
    # 1) archivo de control
    # 2) ejecutable comcot.exe
    # 3) grillas xyz
    # 4) archivo de deformacion de entrada
    # 5) de haber, el archivo ts_location
    # 6) copia el ejecutable de bash que corre la modelacion con wine
    # 1):
    shutil.copy(ctl, dir_ctl) # se copia el ctl
    # 2): 
    shutil.copy("comcot", dir_ctl) # se copia el ejecutable
    # 3):
    for grilla in list(set(glob.glob("*.xyz"))-set(glob.glob("deformacion_*.xyz"))):
        shutil.copy(grilla, dir_ctl) # copiar grillas
    # 4):
    deformacion_input = "deformacion_" + nid_ctl + ".xyz"
    shutil.copy(deformacion_input, dir_ctl)
    # 5):
    if os.path.exists("ts_location.dat"):
        shutil.copy("ts_location.dat", dir_ctl)
    # 6):
    shutil.copy(dir_actual+"/corre_comcot.sh", dir_ctl)
    # cambiar el nombre del archivo de control
    os.chdir(dir_ctl)
    os.rename(ctl, "comcot.ctl")
    os.chdir("..")
    print("creacion directorio para modelacion %s lista") % (nid_ctl)
print("creacion de directorios de modelacion lista")

# se comienza la modelacion
#for dir_ctl in glob.glob("comcot_*/"):
#    os.chdir(dir_ctl)
#    rc = subprocess.call("corre_comcot.sh")









