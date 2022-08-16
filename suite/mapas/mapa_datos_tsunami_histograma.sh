#!/bin/bash

############################################################################################################################################################################
#                                                              INPUT DE USUARIO                                                                                            #
#                                                              INPUT DE USARIO                                                                                             #
############################################################################################################################################################################

#################
# nombre region #
#################
region="mapa_datos_tsunami_resolucion2"

##########################
# Ruta directorio actual #
##########################
diractual=$(pwd)

##########################################
# nombre archivo de datos de deformacion #
##########################################
datafile="alturaMaxenMetros2.txt"

#####################################
# Ruta a archivo con altura de olas #
#####################################
rutadatos=$(pwd)

#################
# datos tsunami #
#################
datatsunami="${rutadatos}/${datafile}"

############################################################################################################################################################################
#                                                              NO MODIFICAR                                                                                                #
#                                                              NO MODIFICAR                                                                                                #
############################################################################################################################################################################
bounds="-80/-70/-48/-31/0/10"
projection="X3.5id/6.5id"
pticks="a2f1SeWn"
sticks="a2f1SEwn"
portrait="-P"	
verbose="-V"
coastline="0.1p,0/0/0"
resolution="f"	
land="-G220"
psfile="${region}.ps"


####################
#basemap and coast
gmt psbasemap -B${pticks} -J${projection} -JZ2i -R${bounds}  -X2 -Y6 ${portrait} ${verbose} -p220/30 -K > ${psfile}
gmt pscoast -B${pticks} -J${projection} -JZ2i -R${bounds} ${portrait} ${verbose}  -D${resolution} -W${coastline} ${land} -p220/30 -O -K >> ${psfile}

# fosa 
gmt psxy SAM.txt -R${bounds} -J${projection} -JZ2i -Sf0.2i/0.1irt -G0 -W0.05c,0 -K -O -V -p220/30 >> ${psfile}

# ploteo datos tsunami
# datos run up
more ${datatsunami} | awk '{print $2-360.0, $3, $4}' | gmt psxyz -J -JZ2i -R -P -V -So0.05i -Wthinner -Gblue -O -Bza2f1+lHeight -p220/30 >> ${psfile}



ps2eps -f ${psfile}
gs -dSAFER -dBATCH -dNOPAUSE -dEPSCrop -r600 -sDEVICE=pngalpha -sOutputFile=${region}.png ${region}.eps
eog ${region}.png &