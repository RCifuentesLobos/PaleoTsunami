#!/bin/bash

############################################################################################################################################################################
#                                                              INPUT DE USUARIO                                                                                            #
#                                                              INPUT DE USARIO                                                                                             #
############################################################################################################################################################################

#################################
# nombre variable al a graficar #
#################################
# elegir entre (sensible a mayusculas y minusculas)
# LN
# LS
# Mw
# AR
# N
varlt="Mw"

###############
# nombre mapa #
###############
region="histograma_${varlt}"
psfile="${region}.ps"

##########################
# Ruta directorio actual #
##########################
diractual=$(pwd)

##########################################
# Ruta a archivos json con parametros lt #
##########################################
rutajson="/home/rodrigo/Documents/Magister/Semestre_III/tesis/paper1/prueba_resolucion2/fallas2/fallas2/modelos_restringidos_magnitud_datos/modelos_restringidos"

#######################################
# cantidad de bins para el histograma #
#######################################
nbins="5"

############################################################################################################################################################################
#                                                              NO MODIFICAR                                                                                                #
#                                                              NO MODIFICAR                                                                                                #
############################################################################################################################################################################

##############################
# datos de formato de json   #
# numero de columna del dato #
##############################
LN="2"
Mw="4"
AR="6"
LS="8"
N="10"

###################################################
# Encontrar los datos para graficar el histograma #
###################################################

# ir al directorio donde estan los readme
cd ${rutajson}

# cantidad de datos
ctdadjson=$(ls readme_* | wc -l)

# leer todos los json
if [[ "$varlt" == "LN" ]]
then
    for json in $(ls readme_*.json);
    do
    more ${json} | sed 's/"//g' | sed 's/{//g' | sed 's/}//g' | sed 's/:/,/g' | awk -F"," -v col=$LN '{print $col}' >> aux.json
    more aux.json | gmt pshistogram -Bxa0.1f0.05+l"${varlt}" -Bya10f5+l"Frequency"+u" %" -BWSne -R-36/-37/0/50 -JX4.8i/2.4i -Gorange -L0.1p -Z1 -W0.05 -V > ${psfile}
    done
elif [[ "$varlt" == "Mw" ]]
then
    for json in $(ls readme_*.json);
    do
    more ${json} | sed 's/"//g' | sed 's/{//g' | sed 's/}//g' | sed 's/:/,/g' | awk -F"," -v col=$Mw '{print $col}' >> aux.json
    more aux.json | gmt pshistogram -Bxa0.1f0.05+l"${varlt}" -Bya10f5+l"Frequency"+u" %" -BWSne -R9.0/9.5/0/50 -JX4.8i/2.4i -Gorange -L0.1p -Z1 -W0.05 -V > ${psfile}
    done
elif [[ "$varlt" == "AR" ]]
then
    for json in $(ls readme_*.json);
    do
    more ${json} | sed 's/"//g' | sed 's/{//g' | sed 's/}//g' | sed 's/:/,/g' | awk -F"," -v col=$AR '{print $col}' >> aux.json
    more aux.json | gmt pshistogram -Bxa0.1f0.05+l"${varlt}" -Bya10f5+l"Frequency"+u" %" -BWSne -R0/3/0/50 -JX4.8i/2.4i -Gorange -L0.1p -Z1 -W0.05 -V > ${psfile}
    done
elif [[ "$varlt" == "LS" ]]
then
    for json in $(ls readme_*.json);
    do
    more ${json} | sed 's/"//g' | sed 's/{//g' | sed 's/}//g' | sed 's/:/,/g' | awk -F"," -v col=$LS '{print $col}' >> aux.json
    more aux.json | gmt pshistogram -Bxa0.1f0.05+l"${varlt}" -Bya10f5+l"Frequency"+u" %" -BWSne -R-45/-46/0/50 -JX4.8i/2.4i -Gorange -L0.1p -Z1 -W0.05 -V > ${psfile}
    done
elif [[ "$varlt" == "N" ]]
then
    for json in $(ls readme_*.json);
    do
    more ${json} | sed 's/"//g' | sed 's/{//g' | sed 's/}//g' | sed 's/:/,/g' | awk -F"," -v col=$N '{print $col}' >> aux.json
    more aux.json | gmt pshistogram -Bxa0.1f0.05+l"${varlt}" -Bya10f5+l"Frequency"+u" %" -BWSne -R15/20/0/50 -JX4.8i/2.4i -Gorange -L0.1p -Z1 -W0.05 -V > ${psfile}
    done
fi

########################
# elementos auxiliares #
########################

rm aux.json
mv ${psfile} ${diractual}
cd ${diractual}
evince ${psfile} &
