#!/bin/bash


############################################################################################################################################################################
#                                                              INPUT DE USUARIO                                                                                            #
#                                                              INPUT DE USARIO                                                                                             #
############################################################################################################################################################################


#################
# nombre region #
#################
region="slip_valdivia_mediana"

##################################
# nombre archivo slip a graficar #
##################################
slipfile="slip_modelo_maxpdf_valdivia.csv"

##########################################
# nombre archivo de datos de deformacion #
##########################################
datafile="def_obs.xyz"

##########################################
# factor de conversion para suma de slip #
##########################################
factor="100"

############################################################################################################################################################################
#                                                              NO MODIFICAR                                                                                                #
#                                                              NO MODIFICAR                                                                                                #
############################################################################################################################################################################

bounds="-81/-67/-49/-34"
projection="M14.0"
pticks="a2f1SeWn"
sticks="a2f1SEwn"
portrait="-P"	
verbose="-V"
coastline="0.5p,0/0/0"
resolution="f"	
land="-G175/175/175"
lakes="-C255/255/255 -A0/2/4"
psfile="${region}.ps"
rests="input/restricciones.csv"
rosa="dg-78/-36+w1c+f+l,,,n"
paleta="/home/rodrigo/Documents/varios/cpt/bath_112.cpt"    #Paleta de colores a usar
paletaslip="/home/rodrigo/Documents/varios/cpt/subtle.cpt"    #Paleta de colores a usar
topografia="/home/rodrigo/Documents/varios/w100s10.Bathymetry.srtm.grd" #Archivo de topografia
ticks="a2f1SeWN"    # Describiendo el marco del mapa
illaz="225"     # Direccion del azimut de iluminacion

###################
# basemap y costa #
###################
gmt psbasemap -B${pticks} -J${projection} -R${bounds}  -X2 -Y6 ${portrait} ${verbose} -K > ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} ${land} -O -K >> ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} ${lakes} -D${resolution} -W${coastline} -O -K >> ${psfile}

###############################################################################
# Cortando la grilla original a los limites establecidos.                     #
# grdcut archivo_entrada.grd -Garchivo_salida.grd -Roeste/este/sur/norte [-V] #
###############################################################################
gmt grdcut ${topografia} -G${nombre_mapa}.grd -R${limites} -V 

############################################################################
# Iluminando la grilla topografica generada en el grdcut desde un azimut   #
# especifico para producir un archivo de intensidad (.int) de iluminacion: #
############################################################################
gmt grdgradient ${nombre_mapa}.grd -G${nombre_mapa}.int -A${illaz} -Nt -M

##########################################################################
# Graficando la topografia de la region seleccionada con su iluminacion: #
##########################################################################
gmt makecpt -C${paleta} -V -T-6000/0/50 -Z  > paletaoceano.cpt
gmt grdimage ${nombre_mapa}.grd -Cpaletaoceano.cpt  -I${nombre_mapa}.int -B${ticks} -J${proyeccion} -R${limites} \
${portrait} ${verbose} -O -K >> ${psfile}

#################
# graficar slip #
#################
more ${slipfile} | awk -F","  '{printf"%2.8f %2.8f %2.8f\n",  $1, $2, $3}' | gmt triangulate -G${slip}.grd -I0.1m/0.1m -R -V
gmt makecpt -C${paletaslip} -T0/50/0.1 -Z > paletaslip.cpt
gmt grdimage ${slip}.grd -Cpaletaslip.cpt -B${pticks} -J${projection} -N -Q -R${bounds} ${portrait} ${verbose} -O -K >> ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} -O -K >> ${psfile}

########
# fosa #
########
gmt psxy SAM.txt -R${bounds} -J${projection} -Sf0.2i/0.1irt -G0 -W0.05c,0 -K -O -V >> ${psfile}
#########
# ridge #
#########
cat ridge.txt | awk '{if (NR>1) print $3, $2}' | gmt psxy -R${bounds} -J${projection} -W2p,0 -B${pticks} -A -O -K >> ${psfile}

#####################
# escala de colores #
#####################
gmt psscale -D7.0c/-1.3c/14.4c/0.5ch -Cpaletaslip.cpt -Ba5f1:"Slip [m]": -O -K -V >> ${psfile}

################################
# graficar perfil de los datos #
################################
gmt psbasemap -Jx1.5/1.35 -R0/2.5/-49/-34 -BNwes -Bxa0.5f0.25g0.5+l"m" -Bya1f1 -P -X14.7 -Y0 -V -O -K >> ${psfile}
more ${datafile} | awk '{printf"%2.8f %2.8f \n", sqrt($4*$4), $3}' | sort -k1 | gmt psxy -J -R -Sg0.2c -G0 -W0.005c,0 -P -V -O -K >> ${psfile}
more ${datafile} | awk '{printf"%2.8f %2.8f \n", sqrt($4*$4), $3}' | sort -k2 | gmt psxy -J -R -W0.5p,0 -P -V -O -K >> ${psfile}

###########################
# graficar perfil de slip #
###########################
more ${slipfile} | awk -F"," -v factor=$factor '{printf" %2.8f %2.8f\n", $2, $3/factor}' | awk '{arr[$1]+=$2}END{for (i in arr) {print i, arr[i]}}' | sort -k1 | awk '{print $2, $1}' | gmt psxy -J -R -Sc0.2c -Gblue -W0.005c,blue -P -V -O -K >> ${psfile}
more ${slipfile} | awk -F"," -v factor=$factor '{printf" %2.8f %2.8f\n", $2, $3/factor}' | awk '{arr[$1]+=$2}END{for (i in arr) {print i, arr[i]}}' | sort -k1 | awk '{print $2, $1}' | gmt psxy -J -R -W0.8p,blue -P -V -O -K >> ${psfile}

###########
# leyenda #
###########
# recuadro
gmt psxy << END -J -R -P -G255 -V -W0.2p -O -K >> ${psfile}
0.01 -47.5
0.01 -48.9
2.49 -48.9
2.49 -47.5
0.01 -47.5
END

# simbolo datos
gmt psxy << END -J -R -P -V -Sg -W0.5p,0 -G0 -O -K -N >> ${psfile}
0.5 -47.8 0.2
END
# linea datos
gmt psxy << EOF -J -R -P -V -W0.5p,0 -O -K -N >> ${psfile}
0.25   -47.8
0.75 -47.8
EOF
# label datos
echo 1 -47.8 "Def. data" | gmt pstext -J -R -P -V -F+f12p,Helvetica-Bold,black+jLM -N -O -K >> ${psfile}

# simbolo slip
gmt psxy << EOF -J -R -P -V -Sc -Gblue -W0.5p,blue -O -K -N >> ${psfile}
0.5 -48.6 0.2
EOF
# linea slip
gmt psxy << END -J -R -P -V -W0.5p,blue -N -O -K >> ${psfile}
0.25   -48.6
0.75 -48.6
END
# label slip
echo 1 -48.6 "Slip profile" | gmt pstext -J -R -P -V -F+f12p,Helvetica-Bold,black+jLM -N -O >> ${psfile}

evince ${psfile} &
