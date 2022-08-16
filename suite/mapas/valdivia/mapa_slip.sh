#!/bin/bash
#script written to plot the station delays in GMT5
for slip in $(ls fallas/modelos_restringidos/csv_files/slip*.csv | awk -F"/" '{print $4}' | awk -F"." '{print $1}');
do

region="${slip}_1960"
bounds="-80/-68/-48/-34"
projection="M8.0"
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
########################################
#p delays
####################
#basemap and coast
gmt psbasemap -B${pticks} -J${projection} -R${bounds}  -X2 -Y6 ${portrait} ${verbose} -K > ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} ${land} -O -K >> ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} ${lakes} -D${resolution} -W${coastline} -O -K >> ${psfile}


# deformacion
#slip="slip_1"
slipfile="fallas/modelos_restringidos/csv_files/${slip}.csv"
more ${slipfile} | awk -F","  '{printf"%1.7f %1.7f %1.7f\n",  $1, $2, $3}' | gmt triangulate -G${slip}.grd -I0.1m/0.1m -R -V
gmt makecpt -Csubtle.cpt -T0/50/0.1 -Z > paletaslip.cpt
gmt grdimage ${slip}.grd -Cpaletaslip.cpt -B${pticks} -J${projection} -N -Q -R${bounds} ${portrait} ${verbose} -O -K >> ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} -O -K >> ${psfile}

# fosa 
gmt psxy SAM.txt -R${bounds} -J${projection} -Sf0.2i/0.1irt -G0 -W0.05c,0 -K -O -V >> ${psfile}
#ridge 
cat ridge.txt | awk '{if (NR>1) print $3, $2}' | gmt psxy -R${bounds} -J${projection} -W2p,0 -B${pticks} -A -O -K >> ${psfile}

# leyendas
more ${rests} | awk -F',' '{if ($1==1960) print $2, $3, $4 }' \
| awk  '{if ($3=="-") printf"%1.1f, %1.1f, %1.1f \n", $1, $2, 0; else printf"%1.1f, %1.1f, %1.1f \n", $1, $2, $3}' \
| awk  '{ if ( $3 >= 0 ) print $0}' | gmt psxy -J -R -P -V -S-0.15c -W1.0p,red3 -O -K >> ${psfile}

more ${rests} | awk -F',' '{if ($1==1960) print $2, $3, $4 }' \
| awk  '{if ($3=="-") printf"%1.1f, %1.1f, %1.1f \n", $1, $2, 0; else printf"%1.1f, %1.1f, %1.1f \n", $1, $2, $3}' \
| awk  '{ if ( $3 < 0 ) print $0}' | gmt psxy -J -R -P -V -Sc0.15c -W1.0p,blue -O -K >> ${psfile}

# recuadro con leyenda
gmt psxy << END -J -R -P -G255 -V -W1.0p -O -K >> ${psfile}
-73 -46
-73 -47
-70 -47
-70 -46
-73 -46
END
gmt psxy << END -J -R -P -V -Sc -W1.0p,blue -O -K >> ${psfile}
-72.7 -46.25 0.2
END
gmt psxy << END -J -R -P -V -S- -W1.0p,red3 -O -K >> ${psfile}
-72.7 -46.75 .2
END
# leyenda
gmt pstext << END -R -J -P -V -F+f6p,Helvetica,black -O -K >> ${psfile}
-71.5 -46.25 Subsidence
-71.5 -46.75 No changes 
END
#titulo
gmt pstext << END -R -J -P -V -F+f8p,Helvetica-bold,black+jMC -N -O -K >> ${psfile}
-71.5 -45.75 Vertical Disp.
END

#more ${deffile} | awk -F"," '{if ($3==0) print $1, $2, "NaN"; else print $1, $2, $3}' | gmt xyz2grd -I0.5s -G${deformacion}.grd -R  

gmt psscale -D3.8c/-1.5c/8c/0.5ch -Cpaletaslip.cpt -Ba10f5:"Slip [m]": -O >> ${psfile}



destino="/media/rodrigo/KINGSTON/magister/EGU/ejemplo_EGU/figuras"

mv ${psfile} ${destino}
echo "copiado ${psfile} a ${destino}"
done
evince ${psfile} &