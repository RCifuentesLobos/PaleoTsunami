#!/bin/bash


region="slip_valdivia_mediana"
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
########################################
#p delays
####################
#basemap and coast
gmt psbasemap -B${pticks} -J${projection} -R${bounds}  -X2 -Y6 ${portrait} ${verbose} -K > ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} ${land} -O -K >> ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} ${lakes} -D${resolution} -W${coastline} -O -K >> ${psfile}


# Cortando la grilla original a los limites establecidos. 
# grdcut archivo_entrada.grd -Garchivo_salida.grd -Roeste/este/sur/norte [-V] 
gmt grdcut ${topografia} -G${nombre_mapa}.grd -R${limites} -V 

# Iluminando la grilla topografica generada en el grdcut desde un azimut 
# especifico para producir un archivo de intensidad (.int) de iluminacion:
gmt grdgradient ${nombre_mapa}.grd -G${nombre_mapa}.int -A${illaz} -Nt -M

# Graficando la topografia de la region seleccionada con su iluminacion:
gmt makecpt -C${paleta} -V -T-6000/0/50 -Z  > paletaoceano.cpt
gmt grdimage ${nombre_mapa}.grd -Cpaletaoceano.cpt  -I${nombre_mapa}.int -B${ticks} -J${proyeccion} -R${limites} \
${portrait} ${verbose} -O -K >> ${psfile}


# fosa 
gmt psxy SAM.txt -R${bounds} -J${projection} -Sf0.2i/0.1irt -G0 -W0.05c,0 -K -O -V >> ${psfile}
#ridge 
cat ridge.txt | awk '{if (NR>1) print $3, $2}' | gmt psxy -R${bounds} -J${projection} -W2p,0 -B${pticks} -A -O -K >> ${psfile}



# deformacion


slipfile="../output/mediana_valdivia.csv"
more ${slipfile} | awk -F","  '{printf"%3.7f %3.7f %3.7f\n",  $1, $2, $3}' | gmt triangulate -G${slip}.grd -I0.5m/0.5m -R -V
gmt makecpt -C${paletaslip} -T10/35/0.5 -Z > paletaslip.cpt
gmt grdimage ${slip}.grd -Cpaletaslip.cpt -B${pticks} -J${projection} -N -Q -R${bounds} ${portrait} ${verbose} -O -K >> ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} -O -K >> ${psfile}

# # leyendas
# more ${rests} | awk -F',' '{if ($1==1960) print $2, $3, $4 }' \
# | awk  '{if ($3=="-") printf"%1.1f, %1.1f, %1.1f \n", $1, $2, 0; else printf"%1.1f, %1.1f, %1.1f \n", $1, $2, $3}' \
# | awk  '{ if ( $3 >= 0 ) print $0}' | gmt psxy -J -R -P -V -S-0.15c -W1.0p,red3 -O -K >> ${psfile}

# more ${rests} | awk -F',' '{if ($1==1960) print $2, $3, $4 }' \
# | awk  '{if ($3=="-") printf"%1.1f, %1.1f, %1.1f \n", $1, $2, 0; else printf"%1.1f, %1.1f, %1.1f \n", $1, $2, $3}' \
# | awk  '{ if ( $3 < 0 ) print $0}' | gmt psxy -J -R -P -V -Sc0.15c -W1.0p,blue -O -K >> ${psfile}

# # recuadro con leyenda
# gmt psxy << END -J -R -P -G255 -V -W1.0p -O -K >> ${psfile}
# -73 -46
# -73 -47
# -70 -47
# -70 -46
# -73 -46
# END
# gmt psxy << END -J -R -P -V -Sc -W1.0p,blue -O -K >> ${psfile}
# -72.7 -46.25 0.2
# END
# gmt psxy << END -J -R -P -V -S- -W1.0p,red3 -O -K >> ${psfile}
# -72.7 -46.75 .2
# END
# # leyenda
# gmt pstext << END -R -J -P -V -F+f6p,Helvetica,black -O -K >> ${psfile}
# -71.5 -46.25 Subsidence
# -71.5 -46.75 No changes
# END
# #titulo
# gmt pstext << END -R -J -P -V -F+f8p,Helvetica-bold,black+jMC -N -O -K >> ${psfile}
# -71.5 -45.75 Vertical Disp.
# END

#more ${deffile} | awk -F"," '{if ($3==0) print $1, $2, "NaN"; else print $1, $2, $3}' | gmt xyz2grd -I0.5s -G${deformacion}.grd -R  

gmt psscale -D7.0c/-1.3c/14.4c/0.5ch -Cpaletaslip.cpt -Ba5f1:"Slip median [m]": -O >> ${psfile}
#-D7.2c/-1.3c/14.4c/0.5ch

#destino="/media/rodrigo/KINGSTON/magister/EGU/ejemplo_EGU/figuras"

#mv ${psfile} ${destino}
#echo "copiado ${psfile} a ${destino}"
#done

evince ${psfile} &