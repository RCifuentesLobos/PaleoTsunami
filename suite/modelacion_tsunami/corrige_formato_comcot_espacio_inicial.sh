#!/bin/bash
# eliminar un espacio en blanco del inicio de cada linea de un archivo de texto


for dir in $(ls -d */);
do  
    cd ${dir} 
    more comcot.ctl | sed 's/^[ \t]//' > temp && mv temp comcot.ctl 
    cd ..
done