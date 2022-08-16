#!/bin/bash

# mapa que muestra la ubicacion de los puntos con datos


region="mapa_datos_tsunami_actualizado"
bounds="-80/-68/-46/-31"
projection="M10.0"
pticks="a2f1SeWn"
sticks="a2f1SEwn"
portrait="-P"	
verbose="-V"
coastline="0.1p,0/0/0"
resolution="f"	
land="-G220"
lakes="-C255/255/255 -A0/2/4"
psfile="${region}.ps"
rests="input/restricciones.csv"
datatsunami="../input/alturaMaxenMetros(3).txt"
rosa="dg-78/-36+w1c+f+l,,,n"
paletarunup="/home/rodrigo/Documents/varios/cpt/scoutie.cpt"
########################################
#p delays
####################
#basemap and coast
gmt psbasemap -B${pticks} -J${projection} -R${bounds}  -X2 -Y6 ${portrait} ${verbose} -K > ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} ${land} -O -K >> ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} ${lakes} -D${resolution} -W${coastline} -O -K >> ${psfile}


# deformacion
#slip="slip_1"
#slipfile="fallas/modelos_restringidos/csv_files/${slip}.csv"
#more ${slipfile} | awk -F","  '{printf"%1.7f %1.7f %1.7f\n",  $1, $2, $3}' | gmt triangulate -G${slip}.grd -I0.1m/0.1m -R -V
gmt makecpt -C${paletarunup} -T0/10/0.25 -Z > paletarunup.cpt
#gmt grdimage ${slip}.grd -Cpaletaslip.cpt -B${pticks} -J${projection} -N -Q -R${bounds} ${portrait} ${verbose} -O -K >> ${psfile}


# # topobatimetria
# paleta="/home/ignacia/Documentos/Rodrigo/magister/Tesis/modelos/paletas/bath_112.cpt"    #Paleta de colores a usar
# topografia="/home/ignacia/Documentos/Rodrigo/Slab/w100s10.Bathymetry.srtm.grd" #Archivo de topografia


# Cortando la grilla original a los limites establecidos. 
# grdcut archivo_entrada.grd -Garchivo_salida.grd -Roeste/este/sur/norte [-V] 
#gmt grdcut ${topografia} -G${nombre_mapa}.grd -R${limites} -V 

# Iluminando la grilla topografica generada en el grdcut desde un azimut 
# especifico para producir un archivo de intensidad (.int) de iluminacion:
#gmt grdgradient ${nombre_mapa}.grd -G${nombre_mapa}.int -A${illaz} -Nt -M

# Graficando la topografia de la region seleccionada con su iluminacion:
#gmt makecpt -C${paleta} -V -T-6000/0/50 -Z  > paletaoceano.cpt
#gmt grdimage ${nombre_mapa}.grd -Cpaletaoceano.cpt  -I${nombre_mapa}.int -B${ticks} -J${proyeccion} -R${limites} \
# ${portrait} ${verbose} -O -K >> ${psfile}

gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} ${lakes} -D${resolution} -W${coastline} -O -K >> ${psfile}
#gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} ${land} -O -K >> ${psfile}


# linea de costa 
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} -O -K >> ${psfile}

# fosa 
gmt psxy SAM.txt -R${bounds} -J${projection} -Sf0.2i/0.1irt -G0 -W0.05c,0 -K -O -V >> ${psfile}
#ridge 
#cat ridge.txt | awk '{if (NR>1) print $3, $2}' | gmt psxy -R${bounds} -J${projection} -W2p,0 -B${pticks} -A -O -K >> ${psfile}

# leyendas
#more ${rests} | awk -F',' '{if ($1==1960) print $2, $3, $4 }' \
#| awk  '{if ($3=="-") printf"%1.1f, %1.1f, %1.1f \n", $1, $2, 0; else printf"%1.1f, %1.1f, %1.1f \n", $1, $2, $3}' \
#| awk  '{ if ( $3 >= 0 ) print $0}' | gmt psxy -J -R -P -V -St0.2c -W1.0p,red3  -O -K >> ${psfile}

#more ${rests} | awk -F',' '{if ($1==1960) print $2, $3, $4 }' \
#| awk  '{if ($3=="-") printf"%1.1f, %1.1f, %1.1f \n", $1, $2, 0; else printf"%1.1f, %1.1f, %1.1f \n", $1, $2, $3}' \
#| awk  '{ if ( $3 < 0 ) print $0}' | gmt psxy -J -R -P -V -St0.2c -W1.0p,red3  -O -K >> ${psfile}

# ploteo datos tsunami
# datos run up
more ${datatsunami} | awk '{print $2-360, $3,$4}' | gmt psxy -J -R -P -V -Cpaletarunup.cpt -Sc0.4c -W0.2p,0 -O -K >> ${psfile}
# datos llegada
#more ${datatsunami} | awk -F"," '{if ($4=="nan") print $2, $3}' | gmt psxy -J -R -P -V -Sc0.2c -W1.0p,red3 -O -K >> ${psfile}
# recuadro con leyenda
# gmt psxy << END -J -R -P -G255 -V -W1.0p -A -O -K >> ${psfile}
# -71. -44.5
# -71. -47.8
# -68.3 -47.8
# -68.3 -44.5
# -71. -44.5
# END
# # leyenda
# gmt psxy << END -J -R -P -V -S+  -W1.0p,midnightblue -O -K >> ${psfile}
# -70.1 -44.75 0.02
# -70.1 -45.3 0.1
# -70.1 -46.1  0.2
# -70.1 -47.15 1
# END
# #titulo
# gmt pstext << END -R -J -P -V -F+f7p,Helvetica-Bold,black+jMC -N -O >> ${psfile}
# -68.75 -44.75 0.1 m
# -68.8 -45.3 0.5 m
# -68.8 -46.1 1 m
# -68.8 -47.15 5 m
# END

#more ${deffile} | awk -F"," '{if ($3==0) print $1, $2, "NaN"; else print $1, $2, $3}' | gmt xyz2grd -I0.5s -G${deformacion}.grd -R  

#gmt psscale -D3.8c/-1.5c/8c/0.5ch -Cpaletaslip.cpt -Ba10f5:"Slip [m]": -O >> ${psfile}
gmt psscale -D11c/4.0c/8.0c/0.5c -Cpaletarunup.cpt -Ba1f0.2:"Height [m]": -O >> ${psfile}

# mapa indentado

#gmt pscoast -Rg -JG280/-36/1.1i -Da -G128 -A5000 -Bg -Wfaint -ECL+gbisque -O -K -X0.5 -Y9  -V >> ${psfile}
#echo ${bounds} | sed 's/\// /g' | awk '{printf"%s %s\n %s %s\n %s %s\n %s %s\n %s %s\n", $1, $3, $2, $3, $2, $4, $1, $4, $1, $3}'    | gmt psxy -R -J -A -W0.5p -O -V >> ${psfile}


ps2eps -f ${psfile}
gs -dSAFER -dBATCH -dNOPAUSE -dEPSCrop -r600 -sDEVICE=pngalpha -sOutputFile=${region}.png ${region}.eps
#evince ${psfile} &
eog ${region}.png &