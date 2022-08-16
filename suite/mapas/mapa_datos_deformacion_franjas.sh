#!/bin/bash

# mapa que muestra la ubicacion de los puntos con datos


region="mapa_datos_deformacion_franjas"
bounds="-78/-72/-48/-34"
projection="M7.0"
pticks="a2f1SeWn"
sticks="a2f1SEwn"
portrait="-P"	
verbose="-V"
coastline="0.1p,0/0/0"
resolution="f"	
land="-G220"
lakes="-C255/255/255 -A0/2/4"
psfile="${region}.ps"
rests="../input/def2_obs.xyz"
paletarunup="/home/rodrigo/Documents/varios/cpt/GMT_panoply.cpt"

limites_franjas=(-36.0 -38.0 -40.0 -42.0 -44.0 -46.0)

###################
# basemap y costa #
###################
gmt psbasemap -B${pticks} -J${projection} -R${bounds}  -X2 -Y6 ${portrait} ${verbose} -K > ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} ${land} -O -K >> ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} ${lakes} -D${resolution} -W${coastline} -O -K >> ${psfile}

# paleta de colores de deformacion
gmt makecpt -C${paletarunup} -T-2/2/0.01 -Z > paletarunup.cpt

gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} ${lakes} -D${resolution} -W${coastline} -O -K >> ${psfile}
#gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} ${land} -O -K >> ${psfile}

# linea de costa 
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} -O -K >> ${psfile}

# fosa 
gmt psxy SAM.txt -R${bounds} -J${projection} -Sf0.2i/0.1irt -G0 -W0.05c,0 -K -O -V >> ${psfile}

# datos deformacion
more ${rests} | awk  '{if ($3<=0) printf"%2.8f, %2.8f, %2.8f \n", $1-360, $2, $3}' | gmt psxy -J -R -P -V -Gblue3 -W0.2p,0 -Si0.5c   -O -K >> ${psfile}


more ${rests} | awk  '{if ($3>0) printf"%2.8f, %2.8f, %2.8f \n", $1-360, $2, $3}'  | gmt psxy -J -R -P -V -Gred3 -St0.5c -W0.2p,0  -O -K >> ${psfile}

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
total_datos=$(more ${rests} | awk '{print $1, $2, $3 }' | wc -l)
# inicializar array
datos_xfranja=() # cantidad total
datos_xfranjaporc=() # cantidad porcentual
for (( i=0; i<${#limites_franjas[@]}-1; i++ ));
do 
lim1=${limites_franjas[$i]}
lim2=${limites_franjas[$(($i+1))]}
datos_xfranja[$i]=$(more ${rests} | awk -v var=$lim1 -v var2=$lim2 '{if ($2<var && $2>=var2) print  $2}' | wc -l)
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
datos_fuera=$(more ${rests} | awk -v var=$limnorte -v var2=$limsur '{if ($2>var || $2<=var2) print  $2 }'  | wc -l)
porcentaje_datos_fuera=$(echo "scale=2; $datos_fuera*100/$total_datos" | bc -l)

################################################################
# escribir en el mapa porcentaje de datos fuera de las franjas #
################################################################
gmt pstext << END -R -J -P -V -F+f11p,Helvetica-Bold,black+jML -N -O -K >> ${psfile}
-77.5 -35 outside: ${porcentaje_datos_fuera} %
END


###############
# adicionales #
###############
# recuadro con leyenda
gmt psxy << END -J -R -P -G255 -V -W1.0p -A -N -O -K >> ${psfile}
-73.9 -47.05
-73.9 -47.95
-72.1 -47.95
-72.1 -47.05
-73.9 -47.05
END
# leyenda I
gmt psxy << END -J -R -P -V -St  -W0.2p,red3 -Gred3 -O -K >> ${psfile}
-73.7 -47.6 0.4
END
gmt psxy << END -J -R -P -V -Si  -W0.2p,blue3 -Gblue3 -O -K >> ${psfile}
-73.7 -47.8 0.4
END
# leyenda II
gmt pstext << END -R -J -P -V -F+f7p,Helvetica-Bold,black+jML -N -O -K >> ${psfile}
-73.4 -47.6 Uplift
-73.4 -47.8 Subsidence
END
# titulo
gmt pstext << END -R -J -P -V -F+f9p,Helvetica-Bold,black+jMC -N -O >> ${psfile}
-73 -47.25 Deformation
END

ps2eps -f ${psfile}
gs -dSAFER -dBATCH -dNOPAUSE -dEPSCrop -r600 -sDEVICE=pngalpha -sOutputFile=${region}.png ${region}.eps
#evince ${psfile} &
rm ${psfile}
rm ${region}.eps
rm *.cpt
cp ${region}.png ../figuras
eog ${region}.png &