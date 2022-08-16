"""
crea el archivo comcot.ctl dada las grillas y parametros determinadas en modela_tsunami.py
"""
import numpy as np 
import csv 



# maneja los archivos de deformacion para modelar tsunami
def crea_comcotctl(archivo_deformacion, ruta_deformacion, lista_nombre_grillas, tiempo_total=14400.000, delta_t=60.0, friccion1 = 0.013, friccion2 = 0.025, salidas_gral = 0 ):
    """
    ENTRADAS: 
    archivo_deformacion: archivo de deformacion que sera utilizado como input para la modelacion de tsunami
    ruta_deformacion: ruta a archivos de deformacion
    lista_nombre_grillas: lista de grillas que seran utilizadas para la modelacion
    id: numero identificador del archivo de deformacion que se esta utilizando
    tiempo_total: tiempo total en segundos de duracion de la modelacion
    delta_t: intervalo de guardado de datos en segundos
    friccion1: valor de friccion de manning para grillas de nivel 2 y 3
    friccion2: valor de friccion de manning para grillas de nivel 4
    salidas_gral: tipo de salidas para guardar: 0: Zmax 1: serie de tiempo (requiere ts_locations.dat) 2: ambas
    """

    """
    PREPARACIONES PREVIAS
    """
    # preparacion archivo de deformacion de entrada
    def_if = str(archivo_deformacion.split("_")[1].split(".")[0]) # formato de nombre es deformacion_n.csv, se guarda solo el valor de n como identificador para crear archivo comcot_n.ctl
    # nombre del archivo ctl que se guardara para cada archivo de deformacion
    nombre_archivo_ctl = "comcot_"+def_if+".ctl"

    # se chequea el tipo de variable de las entradas
    # chequeo tiempo total:
    if not isinstance(tiempo_total,str):
        tiempo_total = str(tiempo_total)
    # chequeo delta_t:
    if not isinstance(delta_t,str):
        delta_t = str(delta_t)
    # chequeo friccion1:
    if not isinstance(friccion1,str):
        friccion1 = str(friccion1)
    # chequeo friccion2:
    if not isinstance(friccion2,str):
        friccion2 = str(friccion2)
    # chequeo salidas_gral:
    if not isinstance(salidas_gral,str):
        salidas_gral = str(salidas_gral)

    
    # archivos de deformacion estan en formato csv, mientras que comcot admite archivos xyz, se realiza esta transformacion
    # se carga el archivo
    # se arma el nombre del archivo con su ruta completa
    if not ruta_deformacion.endswith("/"):
        ruta_archivo_deformacion = ruta_deformacion + "/" + archivo_deformacion
    else:
        ruta_archivo_deformacion = ruta_deformacion + archivo_deformacion
    # se carga el archivo y se formatea
    x,y,z = np.loadtxt(ruta_archivo_deformacion, delimiter = ",", usecols = (0,1,2), unpack = True)
    data = np.stack([x.ravel(), y.ravel(), z.ravel()],axis = 1)
    # se crea el nombre para el archivo xyz 
    archivo_deformacion_xyz = archivo_deformacion.replace("csv","xyz")
    # se guarda el archivo xyz
    np.savetxt(archivo_deformacion_xyz,data,fmt='%2.8f')
    # se borra x y z de la memoria
    del x, y, z
    


    """
    CREACION ARCHIVO
    """
    # creacion encabezado comcot.ctl
    ctl = open(nombre_archivo_ctl,"a")
    ctl.write("#################################################\n")
    ctl.write("#                                               #\n")
    ctl.write("# Control file for COMCOT program (v1.7)        #\n")
    ctl.write("#                                               #\n")
    ctl.write("#################################################\n")
    ctl.write("#--+-----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8\n")
    ctl.write("#===============================================:===============================\n")
    ctl.write("# General Parameters for Simulation             : Value Field                  |\n")
    ctl.write("#===============================================:===============================\n")
    ctl.write("#Job Description: NZ30sec bathymetry, Spherical Coordinates for code testing\n")
    ctl.write("Total run time (Wall clock, seconds)           :  " + tiempo_total + "\n")
    ctl.write("Time interval to Save Data    ( unit: sec )    :  " + delta_t + "\n")
    ctl.write("Output Zmax & TS (0-Max Z;1-Timeseries;2-Both) :  " + salidas_gral + "\n")
    ctl.write("Start Type (0-Cold start; 1-Hot start)         :     0\n")
    ctl.write("Resuming Time If hot start (Seconds)           :   800.00\n")
    ctl.write("Specify Min WaterDepth offshore  (meter)       :    0.00\n")
    ctl.write("Initial Cond. (0:FLT,1:File,2:WM,3:LS,4:FLT+LS):     1\n")
    ctl.write("Specify BC  (0-Open;1-Sponge;2-Wall;3-FACTS)   :     0\n")
    ctl.write("Specify Input Z filename (for BC=3, FACTS)     : mw94_n22_nz_ha.xyt\n")
    ctl.write("Specify Input U filename (for BC=3, FACTS)     : mw94_n22_nz_ua.xyt\n")
    ctl.write("Specify Input V filename (for BC=3, FACTS)     : mw94_n22_nz_va.xyt\n")
    ctl.write("\n")
    ctl.write("#===============================================:===============================\n")
    ctl.write("# Parameters for Fault Model (Segment 01)       :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    ctl.write("No. of FLT Planes (With fault_multi.ctl if >1) :   1\n")
    ctl.write("Fault Rupture Time (seconds)                   :   0.0\n")
    ctl.write("Faulting Option (0: Model; 1- Data;)           :   1\n")
    ctl.write("Focal Depth                             (meter):   17800.000\n")
    ctl.write("Length of source area                   (meter):   208929.613\n")
    ctl.write("Width of source area                    (meter):   81658.2371\n")
    ctl.write("Dislocation of fault plate              (meter):   5.5879\n")
    ctl.write("Strike direction (theta)               (degree):   5.00\n")
    ctl.write("Dip  angle       (delta)               (degree):   22.000\n")
    ctl.write("Slip angle       (lamda)               (degree):   106.000\n")
    ctl.write("Origin of Comp. Domain (Layer 01) (Lat, degree):   -50.0\n")
    ctl.write("Origin of Comp. Domain (Layer 01) (Lon, degree):   278.004\n")
    ctl.write("Epicenter: Latitude                    (degree):   -31.22\n")
    ctl.write("Epicenter: Longitude                   (degree):   287.73\n")
    ctl.write("File Name of Deformation Data                  : " + archivo_deformacion_xyz + "\n")
    ctl.write("Data Format Option (0-COMCOT; 1-MOST; 2-XYZ)   :     2\n")
    ctl.write("\n")
    ctl.write("#===============================================:===============================\n")
    ctl.write("#  Parameters for Wave Maker                    :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    ctl.write("Wave type  ( 1:Solit, 2:given, 3:focusing )    :     1\n")
    ctl.write("FileName of Customized Input (for Type=2)      : fse.dat\n")
    ctl.write("Incident direction( 1:top,2:bt,3:lf,4:rt,5:ob ):     2\n")
    ctl.write("Characteristic Wave Amplitude        (meter)   :     0.500\n")
    ctl.write("Typical Water depth                  (meter)   :  2000.000 \n")
    ctl.write("\n")
    ctl.write("#===============================================:===============================\n")
    ctl.write("#  Parameters for Submarine LS/Transient Motion :ValUes                        |\n")
    ctl.write("#===============================================:===============================\n")
    ctl.write("X Coord. of Left/West Edge of Landlide Area    :  177.00\n")
    ctl.write("X Coord. of Right/East Edge of Landlide Area   :  179.00\n")
    ctl.write("Y Coord. of Bottom/South Edge of Landlide Area :  -41.00\n")
    ctl.write("Y Coord. of Top/North Edge of Landlide Area    :  -39.00\n")
    ctl.write("File Name of landslide Data                    : landslide_test.dat\n")
    ctl.write("Data Format Option (0-Old; 1-XYT; 2-Function)  :     2\n")
    ctl.write(" \n")
    ctl.write("#===============================================:===============================\n")
    ctl.write("# Configurations for all grids                  :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    ctl.write("# Parameters for 1st-level grid -- layer 01     :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    if "ccg1_salida.xyz" in lista_nombre_grillas:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     0\n")
    else:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Coordinate System    (0:spherical, 1:cartesian):     0\n")
    ctl.write(" Governing Equations  (0:linear,    1:nonlinear):     0\n")
    ctl.write(" Grid Size  (dx, sph:minute, cart:meter)        :     2.16\n")
    ctl.write(" Time step                            ( second ):     1.0\n")
    ctl.write(" Bottom Friction Switch? (0:Yes,1:No,2:var. n ) :     1\n")
    ctl.write(" Manning's Roughness Coef. (For fric.option=0)  :     " + friccion1 + "\n")
    ctl.write(" Layer Ouput Option? (0:Z+Hu+Hv;1:Z Only;2:NONE):     1\n")
    ctl.write(" X_start                                        :     279.9494\n")
    ctl.write(" X_end                                          :     290.0294\n")
    ctl.write(" Y_Start                                        :     -46.008\n")
    ctl.write(" Y_end                                          :     -33.156\n")
    ctl.write(" File Name of Bathymetry Data                   : ccg1_salida.xyz\n")
    ctl.write(" Data Format Option (0-OLD;1-MOST;2-XYZ;3-ETOPO):     2\n")
    ctl.write(" Grid Identification Number                     :    01\n")
    ctl.write(" Grid Level                                     :     1\n")
    ctl.write(" Parent Grid's ID Number                        :    -1\n")
    ctl.write("\n")
    ctl.write("#===============================================:=============================== \n")
    ctl.write("#  Parameters for Sub-level grid -- layer 02    :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    if "chiloe_036m_salida.xyz" in lista_nombre_grillas:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     0\n")
    else:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Coordinate           (0:spherical, 1:cartesian):     0\n")
    ctl.write(" Governing Eqn.       (0:linear,    1:nonlinear):     0\n")
    ctl.write(" Bottom Friction Switch? (0:Yes,1:No,2:var. n ) :     1\n")
    ctl.write(" Manning's Roughness Coef. (For fric.option=0)  :     " + friccion1 + "\n")
    ctl.write(" Layer Ouput Option? (0:Z+Hu+Hv;1:Z Only;2:NONE):     1\n")
    ctl.write(" GridSize Ratio of Parent layer to current layer:     6\n")
    ctl.write(" X_start                                        : 284.8706\n")
    ctl.write(" X_end                                          : 287.5946\n")
    ctl.write(" Y_start                                        : -43.7336\n")
    ctl.write(" Y_end                                          : -40.7516\n")
    ctl.write(" FileName of Water depth data                   : chiloe_036m_salida.xyz\n")
    ctl.write(" Data Format Option (0-OLD;1-MOST;2-XYZ;3-ETOPO):     2\n")
    ctl.write(" Grid Identification Number                     :    02\n")
    ctl.write(" Grid Level                                     :     2\n")
    ctl.write(" Parent Grid's ID Number                        :    01\n")
    ctl.write("\n")
    ctl.write("#===============================================:=============================== \n")
    ctl.write("#  Parameters for Sub-level grid -- layer 03    :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    if "Ancud_n3_0108msalida.xyz" in lista_nombre_grillas:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     0\n")
    else:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Coordinate           (0:spherical, 1:cartesian):     0\n")
    ctl.write(" Governing Eqn.       (0:linear,    1:nonlinear):     1\n")
    ctl.write(" Bottom Friction Switch? (0:Yes,1:No,2:var. n ) :     1\n")
    ctl.write(" Manning's Roughness Coef. (For fric.option=0)  :     " + friccion1 + "\n")
    ctl.write(" Layer Ouput Option? (0:Z+Hu+Hv;1:Z Only;2:NONE):     1\n")
    ctl.write(" GridSize Ratio of Parent layer to current layer:     5\n")
    ctl.write(" X_start                                        :  285.9638\n")
    ctl.write(" X_end                                          :  286.4012\n")
    ctl.write(" Y_start                                        :  -41.9435\n")
    ctl.write(" Y_end                                          :  -41.6519\n")
    ctl.write(" FileName of Water depth data                   : Ancud_n3_0108msalida.xyz\n")
    ctl.write(" Data Format Option (0-OLD;1-MOST;2-XYZ;3-ETOPO):     2 \n")
    ctl.write(" Grid Identification Number                     :    03\n")
    ctl.write(" Grid Level                                     :     3\n")
    ctl.write(" Parent Grid's ID Number                        :    02 \n")
    ctl.write(" \n")
    ctl.write("#===============================================:=============================== \n")
    ctl.write("#  Parameters for Sub-level grid -- layer 04    :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    if "Ancud_n4_0054m_final.xyz" in lista_nombre_grillas:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     0\n")
    else:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Coordinate           (0:spherical, 1:cartesian):     0\n")
    ctl.write(" Governing Eqn.       (0:linear,    1:nonlinear):     1\n")
    ctl.write(" Bottom Friction Switch? (0:Yes,1:No,2:var. n ) :     0\n")
    ctl.write(" Manning's Roughness Coef. (For fric.option=0)  :     " + friccion2 + "\n")
    ctl.write(" Layer Ouput Option? (0:Z+Hu+Hv;1:Z Only;2:NONE):     1\n")
    ctl.write(" GridSize Ratio of Parent layer to current layer:     2\n")
    ctl.write(" X_start                                        :    285.9860\n")
    ctl.write(" X_end                                          :    286.2578\n")
    ctl.write(" Y_start                                        :    -41.9120\n")
    ctl.write(" Y_end                                          :    -41.7590\n")
    ctl.write(" FileName of Water depth data                   : Ancud_n4_0054m_final.xyz\n")
    ctl.write(" Data Format Option (0-OLD;1-MOST;2-XYZ;3-ETOPO):     2\n")
    ctl.write(" Grid Identification Number                     :    04\n")
    ctl.write(" Grid Level                                     :     4\n")
    ctl.write(" Parent Grid's ID number                        :    03 \n")
    ctl.write(" \n")
    ctl.write("#===============================================:=============================== \n")
    ctl.write("#  Parameters for Sub-level grid -- layer 05    :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    if "maullin_n4_0036_salida.xyz" in lista_nombre_grillas:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     0\n")
    else:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Coordinate           (0:spherical, 1:cartesian):     0\n")
    ctl.write(" Governing Eqn.       (0:linear,    1:nonlinear):     0\n")
    ctl.write(" Bottom Friction Switch? (0:Yes,1:No,2:var. n ) :     1\n")
    ctl.write(" Manning's Roughness Coef. (For fric.option=0)  :     " + friccion1 + "\n")
    ctl.write(" Layer Ouput Option? (0:Z+Hu+Hv;1:Z Only;2:NONE):     1\n")
    ctl.write(" GridSize Ratio of Parent layer to current layer:     3\n")
    ctl.write(" X_start                                        :    286.3437\n")
    ctl.write(" X_end                                          :    286.4211\n")
    ctl.write(" Y_start                                        :    -41.6373\n")
    ctl.write(" Y_end                                          :    -41.5773\n")
    ctl.write(" FileName of Water depth data                   :  maullin_n4_0036_salida.xyz\n")
    ctl.write(" Data Format Option (0-OLD;1-MOST;2-XYZ;3-ETOPO):     2\n")
    ctl.write(" Grid Identification Number                     :    05\n")
    ctl.write(" Grid Level                                     :     4\n")
    ctl.write(" Parent Grid's ID number                        :    03 \n")
    ctl.write(" \n")
    ctl.write("#===============================================:=============================== \n")
    ctl.write("#  Parameters for Sub-level grid -- layer 06    :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    if "Arauco_n3_009m.xyz" in lista_nombre_grillas:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     0\n")
    else:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Coordinate           (0:spherical, 1:cartesian):     0\n")
    ctl.write(" Governing Eqn.       (0:linear,    1:nonlinear):     1\n")
    ctl.write(" Bottom Friction Switch? (0:Yes,1:No,2:var. n ) :     1\n")
    ctl.write(" Manning's Roughness Coef. (For fric.option=0)  :     " + friccion1 + "\n")
    ctl.write(" Layer Ouput Option? (0:Z+Hu+Hv;1:Z Only;2:NONE):     1\n")
    ctl.write(" GridSize Ratio of Parent layer to current layer:     24\n")
    ctl.write(" X_start                                        :   286.355\n")
    ctl.write(" X_end                                          :   286.895\n")
    ctl.write(" Y_start                                        :   -37.3225\n")
    ctl.write(" Y_end                                          :   -36.7195\n")
    ctl.write(" FileName of Water depth data                   : Arauco_n3_009m.xyz\n")
    ctl.write(" Data Format Option (0-OLD;1-MOST;2-XYZ;3-ETOPO):     2\n")
    ctl.write(" Grid Identification Number                     :    06\n")
    ctl.write(" Grid Level                                     :     2\n")
    ctl.write(" Parent Grid's ID number                        :    01\n")
    ctl.write(" \n")
    ctl.write("#===============================================:=============================== \n")
    ctl.write("#  Parameters for Sub-level grid -- layer 07    :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    if "Corral_n3_009m.xyz" in lista_nombre_grillas:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     0\n")
    else:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Coordinate           (0:spherical, 1:cartesian):     0\n")
    ctl.write(" Governing Eqn.       (0:linear,    1:nonlinear):     1\n")
    ctl.write(" Bottom Friction Switch? (0:Yes,1:No,2:var. n ) :     0\n")
    ctl.write(" Manning's Roughness Coef. (For fric.option=0)  :     " + friccion2 + "\n")
    ctl.write(" Layer Ouput Option? (0:Z+Hu+Hv;1:Z Only;2:NONE):     1\n")
    ctl.write(" GridSize Ratio of Parent layer to current layer:     24\n")
    ctl.write(" X_start                                        :   286.5217\n")
    ctl.write(" X_end                                          :   286.6657\n")
    ctl.write(" Y_start                                        :   -39.9492\n")
    ctl.write(" Y_end                                          :   -39.7917\n")
    ctl.write(" FileName of Water depth data                   : Corral_n3_009m.xyz\n")
    ctl.write(" Data Format Option (0-OLD;1-MOST;2-XYZ;3-ETOPO):     2\n")
    ctl.write(" Grid Identification Number                     :    07\n")
    ctl.write(" Grid Level                                     :     2\n")
    ctl.write(" Parent Grid's ID number                        :    01 \n")
    ctl.write("\n")
    ctl.write("#===============================================:=============================== \n")
    ctl.write("#  Parameters for Sub-level grid -- layer 08    :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    if "Corral_n4_0045salida.xyz" in lista_nombre_grillas:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     0\n")
    else:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Coordinate           (0:spherical, 1:cartesian):     0\n")
    ctl.write(" Governing Eqn.       (0:linear,    1:nonlinear):     0\n")
    ctl.write(" Use Bottom friction ?(only cart,nonlin,0:y,1:n):     1\n")
    ctl.write(" Manning's Roughness Coef. (For fric.option=0)  :     " + friccion1 + "\n")
    ctl.write(" Layer Ouput Option? (0:Z+Hu+Hv;1:Z Only;2:NONE):     1\n")
    ctl.write(" GridSize Ratio of Parent layer to current layer:     2\n")
    ctl.write(" X_start                                        :   286.5616\n")
    ctl.write(" X_end                                          :   286.6006\n")
    ctl.write(" Y_start                                        :   -39.8959\n")
    ctl.write(" Y_end                                          :   -39.8681\n")
    ctl.write(" FileName of Water depth data                   : Corral_n4_0045salida.xyz\n")
    ctl.write(" Data Format Option (0-OLD;1-MOST;2-XYZ;3-ETOPO):     2\n")
    ctl.write(" Grid Identification Number                     :    08\n")
    ctl.write(" Grid Level                                     :     3\n")
    ctl.write(" Parent Grid's ID number                        :    07\n")
    ctl.write(" \n")
    ctl.write("#===============================================:=============================== \n")
    ctl.write("#  Parameters for Sub-level grid -- layer 09    :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    if "G3_bahias_018m.xyz" in lista_nombre_grillas:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     0\n")
    else:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Coordinate           (0:spherical, 1:cartesian):     1\n")
    ctl.write(" Governing Eqn.       (0:linear,    1:nonlinear):     1\n")
    ctl.write(" Bottom Friction Switch? (0:Yes,1:No,2:var. n ) :     1\n")
    ctl.write(" Manning's Roughness Coef. (For fric.option=0)  :     0.025\n")
    ctl.write(" Layer Ouput Option? (0:Z+Hu+Hv;1:Z Only;2:NONE):     1\n")
    ctl.write(" GridSize Ratio of Parent layer to current layer:     2\n")
    ctl.write(" X_start                                        :   286.350000\n")
    ctl.write(" X_end                                          :   286.812000\n")
    ctl.write(" Y_start                                        :   -42.006000\n")
    ctl.write(" Y_end                                          :   -41.700000\n")
    ctl.write(" FileName of Water depth data                   : G3_bahias_018m.xyz\n")
    ctl.write(" Data Format Option (0-OLD;1-MOST;2-XYZ;3-ETOPO):     2\n")
    ctl.write(" Grid Identification Number                     :    09\n")
    ctl.write(" Grid Level                                     :     3\n")
    ctl.write(" Parent Grid's ID number                        :    02\n")
    ctl.write(" \n")
    ctl.write("#===============================================:=============================== \n")
    ctl.write("#  Parameters for Sub-level grid -- layer 12    :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    if "G4_bahias_009m.xyz" in lista_nombre_grillas:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     0\n")
    else:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Coordinate           (0:spherical, 1:cartesian):     1\n")
    ctl.write(" Governing Eqn.       (0:linear,    1:nonlinear):     1\n")
    ctl.write(" Bottom Friction Switch? (0:Yes,1:No,2:var. n ) :     1\n")
    ctl.write(" Manning's Roughness Coef. (For fric.option=0)  :     0.025\n")
    ctl.write(" Layer Ouput Option? (0:Z+Hu+Hv;1:Z Only;2:NONE):     1\n")
    ctl.write(" GridSize Ratio of Parent layer to current layer:     2\n")
    ctl.write(" X_start                                        :  286.4203\n")
    ctl.write(" X_end                                          :  286.5883\n")
    ctl.write(" Y_start                                        :   -41.9831\n")
    ctl.write(" Y_end                                          :   -41.7821\n")
    ctl.write(" FileName of Water depth data                   : G4_bahias_009m.xyz\n")
    ctl.write(" Data Format Option (0-OLD;1-MOST;2-XYZ;3-ETOPO):     2\n")
    ctl.write(" Grid Identification Number                     :    10\n")
    ctl.write(" Grid Level                                     :     4\n")
    ctl.write(" Parent Grid's ID number                        :    09\n")
    ctl.write(" \n")
    ctl.write("#===============================================:=============================== \n")
    ctl.write("#  Parameters for Sub-level grid -- layer 11    :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    if "G3_Quemchi_0072m.xyz" in lista_nombre_grillas:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     0\n")
    else:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Coordinate           (0:spherical, 1:cartesian):     1\n")
    ctl.write(" Governing Eqn.       (0:linear,    1:nonlinear):     1\n")
    ctl.write(" Bottom Friction Switch? (0:Yes,1:No,2:var. n ) :     1\n")
    ctl.write(" Manning's Roughness Coef. (For fric.option=0)  :     0.025\n")
    ctl.write(" Layer Ouput Option? (0:Z+Hu+Hv;1:Z Only;2:NONE):     1\n")
    ctl.write(" GridSize Ratio of Parent layer to current layer:     5\n")
    ctl.write(" X_start                                        :   286.5\n")
    ctl.write(" X_end                                          :   286.6752\n")
    ctl.write(" Y_start                                        :   -42.22\n")
    ctl.write(" Y_end                                          :   -42.0688\n")
    ctl.write(" FileName of Water depth data                   : G3_Quemchi_0072m.xyz\n")
    ctl.write(" Data Format Option (0-OLD;1-MOST;2-XYZ;3-ETOPO):     2\n")
    ctl.write(" Grid Identification Number                     :    11\n")
    ctl.write(" Grid Level                                     :     3\n")
    ctl.write(" Parent Grid's ID number                        :    02\n")
    ctl.write(" \n")
    ctl.write("#===============================================:=============================== \n")
    ctl.write("#  Parameters for Sub-level grid -- layer 12    :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    if "G4_bahias_009m.xyz" in lista_nombre_grillas:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     0\n")
    else:
        ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Coordinate           (0:spherical, 1:cartesian):     1\n")
    ctl.write(" Governing Eqn.       (0:linear,    1:nonlinear):     1\n")
    ctl.write(" Bottom Friction Switch? (0:Yes,1:No,2:var. n ) :     1\n")
    ctl.write(" Manning's Roughness Coef. (For fric.option=0)  :     0.025\n")
    ctl.write(" Layer Ouput Option? (0:Z+Hu+Hv;1:Z Only;2:NONE):     1\n")
    ctl.write(" GridSize Ratio of Parent layer to current layer:     2\n")
    ctl.write(" X_start                                        :   286.513\n")
    ctl.write(" X_end                                          :   286.5670\n")
    ctl.write(" Y_start                                        :   -42.1698\n")
    ctl.write(" Y_end                                          :   -42.126\n")
    ctl.write(" FileName of Water depth data                   : G4_Quemchi_0036m.xyz\n")
    ctl.write(" Data Format Option (0-OLD;1-MOST;2-XYZ;3-ETOPO):     2\n")
    ctl.write(" Grid Identification Number                     :    12\n")
    ctl.write(" Grid Level                                     :     4\n")
    ctl.write(" Parent Grid's ID number                        :    11\n")
    ctl.write(" \n")
    ctl.write("#===============================================:=============================== \n")
    ctl.write("#  Parameters for Sub-level grid -- layer 13    :Values                        |\n")
    ctl.write("#===============================================:===============================\n")
    ctl.write(" Run This Layer ?       (0:Yes,       1:No     ):     1\n")
    ctl.write(" Coordinate           (0:spherical, 1:cartesian):     1\n")
    ctl.write(" Governing Eqn.       (0:linear,    1:nonlinear):     0\n")
    ctl.write(" Bottom Friction Switch? (0:Yes,1:No,2:var. n ) :     1\n")
    ctl.write(" Manning's Roughness Coef. (For fric.option=0)  :     0.013\n")
    ctl.write(" Layer Ouput Option? (0:Z+Hu+Hv;1:Z Only;2:NONE):     1\n")
    ctl.write(" GridSize Ratio of Parent layer to current layer:     5\n")
    ctl.write(" X_start                                        :    41.\n")
    ctl.write(" X_end                                          :    60.\n")
    ctl.write(" Y_start                                        :    41.\n")
    ctl.write(" Y_end                                          :    60.\n")
    ctl.write(" FileName of Water depth data                   : layer44.dep\n")
    ctl.write(" Data Format Option (0-OLD;1-MOST;2-XYZ;3-ETOPO):     0 \n")
    ctl.write(" Grid Identification Number                     :    13\n")
    ctl.write(" Grid Level                                     :     2\n")
    ctl.write(" Parent Grid's ID number                        :    01\n")
    ctl.write(" \n")

    ctl.close()
 

