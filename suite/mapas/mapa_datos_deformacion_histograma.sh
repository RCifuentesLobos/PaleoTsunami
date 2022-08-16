#!/bin/bash

############################################################################################################################################################################
#                                                              INPUT DE USUARIO                                                                                            #
#                                                              INPUT DE USARIO                                                                                             #
############################################################################################################################################################################

#################
# nombre region #
#################
region="mapa_datos_deformacion_resolucion1"

##########################
# Ruta directorio actual #
##########################
diractual=$(pwd)

##########################################
# nombre archivo de datos de deformacion #
##########################################
datafile="def_obs.xyz"

#####################################
# Ruta a archivo con altura de olas #
#####################################
rutadatos=$(pwd)

#################
# datos tsunami #
#################
datadef="${rutadatos}/${datafile}"

############################################################################################################################################################################
#                                                              NO MODIFICAR                                                                                                #
#                                                              NO MODIFICAR                                                                                                #
############################################################################################################################################################################
bounds="-78/-70/-48/-34/0/1"
projection="X3.1id/6.5id"
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

# ploteo datos deformacion
# datos surgencia
more ${datadef} | awk '{if ($4>=0) print $2, $3, $4}' | gmt psxyz -J -JZ2i -R -P -V -So0.05i -Wthinner -Gblue -O -K -Bza0.2f0.1+lHeight -p220/30 >> ${psfile}
# datos subsidencia
more ${datadef} | awk '{if ($4<0) print $2, $3, -1*$4}' | gmt psxyz -J -JZ2i -R -P -V -So0.05i -Wthinner -Gred -O -K -Bza0.2f0.1+lHeight -p220/30 >> ${psfile}

gmt pslegend << END -R -J -JZ -DjLB+o0.2i+w1.0i/0+jBL -O -V --FONT=Helvetica-Bold -F+glightgrey+pthinner+s-4p/-6p/grey20@40 -p  >> ${psfile}
G 0.1c
L 10 Helvetica-Bold L Deformation
D 0.05c 1p
G 0.01c
C 0/0/255
L 10 Helvetica-Bold L Uplift
C 255/0/0
L 10 Helvetica-Bold L Subsidence
END


ps2eps -f ${psfile}
gs -dSAFER -dBATCH -dNOPAUSE -dEPSCrop -r600 -sDEVICE=pngalpha -sOutputFile=${region}.png ${region}.eps
eog ${region}.png &