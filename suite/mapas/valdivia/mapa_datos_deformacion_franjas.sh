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
rests="../input/restricciones.csv"
paletarunup="/home/rodrigo/Documents/varios/cpt/GMT_panoply.cpt"

limites_franjas=(-36.0 -38.0 -40.0 -42.0 -44.0 -46.0)

####################
#basemap and coast
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
more ${rests} | awk -F',' '{if ($1==1960) print $2, $3, $4 }' \
| awk  '{if ($3=="-") printf"%1.1f, %1.1f, %1.1f \n", $1, $2, 0; else printf"%1.1f, %1.1f, %1.1f \n", $1, $2, $3}' \
| awk  '{ if ( $3 >= 0 ) print $0}' | gmt psxy -J -R -P -V -Gred3 -W0.2p,0 -Sl0.8c+t~   -O -K >> ${psfile}

#gmt psxy -J -R -P -V -Sl0.4c+t~ -Gmidnightblue -O -K >> ${psfile}
more ${rests} | awk -F',' '{if ($1==1960) print $2, $3, $4 }' \
| awk  '{if ($3=="-") printf"%1.1f, %1.1f, %1.1f \n", $1, $2, 0; else printf"%1.1f, %1.1f, %1.1f \n", $1, $2, $3}' \
| awk  '{ if ( $3 < 0 ) print $0}' | gmt psxy -J -R -P -V -Gblue3 -Si0.5c -W0.2p,0  -O -K >> ${psfile}


# franjas 
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

# contar cuantos datos hay en cada franja y calcular el porcentaje total
total_datos=$(more ${rests} | awk -F',' '{if ($1==1960) print $2, $3, $4 }' | wc -l)
# inicializar array
datos_xfranja=() # cantidad total
datos_xfranjaporc=() # cantidad porcentual
for (( i=0; i<${#limites_franjas[@]}-1; i++ ));
do 
lim1=${limites_franjas[$i]}
lim2=${limites_franjas[$(($i+1))]}
datos_xfranja[$i]=$(more ${rests} | awk -F',' -v var=$lim1 -v var2=$lim2 '{if ($1==1960 && $3<var && $3>=var2) print  $3 }' | wc -l)
datos_xfranjaporc[$i]=$(echo "scale=2; ${datos_xfranja[$i]}*100/$total_datos" | bc )
done

# escribir en el mapa el porcentaje de datos
for (( i=0; i<${#limites_franjas[@]}-1; i++ ));
do 
promediolat=$(echo "scale=2;  ${limites_franjas[$i]}/2+${limites_franjas[$i+1]}/2" | bc)
gmt pstext << END -R -J -P -V -F+f11p,Helvetica-Bold,black+jML -N -O -K >> ${psfile}
-77.5 ${promediolat} ${datos_xfranjaporc[$i]} %
END
done 


# recuadro con leyenda
gmt psxy << END -J -R -P -G255 -V -W1.0p -A -N -O -K >> ${psfile}
-73.9 -46.05
-73.9 -46.95
-72.1 -46.95
-72.1 -46.05
-73.9 -46.05
END
# leyenda
gmt psxy << END -J -R -P -V -Sl+t~  -W0.2p,red3 -Gred3 -O -K >> ${psfile}
-73.7 -46.6 0.4
END
gmt psxy << END -J -R -P -V -Si  -W0.2p,blue3 -Gblue3 -O -K >> ${psfile}
-73.7 -46.8 0.4
END
#titulo
gmt pstext << END -R -J -P -V -F+f7p,Helvetica-Bold,black+jML -N -O -K >> ${psfile}
-73.4 -46.6 No change
-73.4 -46.8 Subsidence
END

gmt pstext << END -R -J -P -V -F+f9p,Helvetica-Bold,black+jMC -N -O >> ${psfile}
-73 -46.25 Deformation
END

ps2eps -f ${psfile}
gs -dSAFER -dBATCH -dNOPAUSE -dEPSCrop -r600 -sDEVICE=pngalpha -sOutputFile=${region}.png ${region}.eps
#evince ${psfile} &
rm ${psfile}
rm ${region}.eps
rm *.cpt
eog ${region}.png &