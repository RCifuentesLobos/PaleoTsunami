#!/bin/bash

# copia todos los directorios comcot_* a un directorio de destino para ordenar la modelacion

# definir directorio de destino 
dir_destino="modelacion_orden_ctdad_datos"


for d in $(ls); do 
if [[ -d $d ]]; 
then  
if [[ $d == comcot_* ]]; 
then 
echo $d; 
cp -aR $d $dir_destino
fi; 
fi; 
done