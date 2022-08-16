#!/bin/bash

# transforma los archivos de deformacion de formato csv a xyz para ser utilizados como input en comcot

for csv in $(ls -f deformacion_*.csv);
do
    nombre=$(echo ${csv} | awk -F"." '{print $1}')
    more ${csv} | awk -F"," '{printf"%3.10f %3.10f %3.10f \n", $1+360, $2, $3}' > ${nombre}.xyz
    mv ${nombre}.xyz xyz_files
done