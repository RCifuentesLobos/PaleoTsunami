#!/bin/bash

# mapa que muestra la ubicacion de los puntos con datos


region="mapa_datos_tsunami_franjas"
bounds="-80/-70/-48/-31"
projection="M8.0"
pticks="a2f1SeWn"
sticks="a2f1SEwn"
portrait="-P"	
verbose="-V"
coastline="0.1p,0/0/0"
resolution="f"	
land="-G220"
lakes="-C255/255/255 -A0/2/4"
psfile="${region}.ps"
datatsunami="../input/alturaMaxenMetros2.txt"
paletarunup="/home/rodrigo/Documents/varios/cpt/scoutie.cpt"

limites_franjas=(-36.0 -38.0 -40.0 -42.0 -44.0 -46.0)

####################
# basemap y costa  #
####################
gmt psbasemap -B${pticks} -J${projection} -R${bounds}  -X2 -Y6 ${portrait} ${verbose} -K > ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} ${land} -O -K >> ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} ${lakes} -D${resolution} -W${coastline} -O -K >> ${psfile}

# paleta de colores
gmt makecpt -C${paletarunup} -T0/25/0.25 -Z > paletarunup.cpt

gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} ${lakes} -D${resolution} -W${coastline} -O -K >> ${psfile}

# linea de costa 
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} -O -K >> ${psfile}

# fosa 
gmt psxy SAM.txt -R${bounds} -J${projection} -Sf0.2i/0.1irt -G0 -W0.05c,0 -K -O -V >> ${psfile}

# ploteo datos tsunami
# datos run up
more ${datatsunami} | awk '{print $2, $3, $4}' | gmt psxy -J -R -P -V -Cpaletarunup.cpt -Sc0.4c -W0.2p,0 -O -K >> ${psfile}
###########
# franjas #
########### 
for i in ${!limites_franjas[@]};
do 
if [[ $i -eq 0 ]] || [[ $i -eq 5 ]];
then
gmt psxy << END -J -R -P -G255 -V -W1.0p -A -N -O -K >> ${psfile}
-77.5 ${limites_franjas[$i]}
-72.5 ${limites_franjas[$i]}
END
else 
gmt psxy << END -J -R -P -G255 -V -W1.0p,. -A -N -O -K >> ${psfile}
-77.5 ${limites_franjas[$i]}
-72.5 ${limites_franjas[$i]}
END
fi
done

##########################################################################
# contar cuantos datos hay en cada franja y calcular el porcentaje total #
##########################################################################
total_datos=$(more ${datatsunami} | awk '{print $2, $3, $4 }' | wc -l)
# inicializar array
datos_xfranja=() # cantidad total
datos_xfranjaporc=() # cantidad porcentual
for (( i=0; i<${#limites_franjas[@]}-1; i++ ));
do 
lim1=${limites_franjas[$i]}
lim2=${limites_franjas[$(($i+1))]}
datos_xfranja[$i]=$(more ${datatsunami} | awk -v var=$lim1 -v var2=$lim2 '{if ($3<var && $3>=var2) print  $3 }' | wc -l)
datos_xfranjaporc[$i]=$(echo "scale=2; ${datos_xfranja[$i]}*100/$total_datos" | bc )
done

##############################################
# escribir en el mapa el porcentaje de datos #
##############################################
for (( i=0; i<${#limites_franjas[@]}-1; i++ ));
do 
promediolat=$(echo "scale=2;  ${limites_franjas[$i]}/2+${limites_franjas[$i+1]}/2" | bc)
gmt pstext << END -R -J -P -V -F+f11p,Helvetica-Bold,black+jML -N -O -K >> ${psfile}
-77.5 ${promediolat} ${datos_xfranjaporc[$i]} %
END
done 

##########################################
# porcentaje de datos fuera de la franja #
##########################################
limnorte=${limites_franjas[0]}
limsur=${limites_franjas[5]}
datos_fuera=$(more ${datatsunami}  | awk -v var=$limnorte -v var2=$limsur '{if ($3>var || $3<=var2) print  $3 }'  | wc -l)
porcentaje_datos_fuera=$(echo "scale=2; $datos_fuera*100/$total_datos" | bc -l)

################################################################
# escribir en el mapa porcentaje de datos fuera de las franjas #
################################################################
gmt pstext << END -R -J -P -V -F+f11p,Helvetica-Bold,black+jML -N -O -K >> ${psfile}
-77.5 -33 outside: ${porcentaje_datos_fuera} %
END

# escala
gmt psscale -D11c/4.0c/8.0c/0.5c -Cpaletarunup.cpt -Ba5f1:"Height [m]": -O >> ${psfile}



ps2eps -f ${psfile}
gs -dSAFER -dBATCH -dNOPAUSE -dEPSCrop -r600 -sDEVICE=pngalpha -sOutputFile=${region}.png ${region}.eps
rm ${psfile}
rm ${region}.eps
rm *.cpt
cp ${region}.png ../figuras
eog ${region}.png &
