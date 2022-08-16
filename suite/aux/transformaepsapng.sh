#!/bin/bash


for i in $(ls *.eps);
do
png=$(echo $i | awk -F"." '{print $1}')
gs -dSAFER -dBATCH -dNOPAUSE -dEPSCrop -r600 -sDEVICE=pngalpha -sOutputFile=$png.png $i
done