#!/bin/bash

# Subset ocean color data to make data extraction at CTD locations faster
# Time-stamp: <2021-12-01 13:19:22 ivan>

# # Chl daily data
datadir="/bali/data/ilima/Satellite_Data/Ocean_Color/Chl/daily"
outdir="/home/ivan/Data/Postproc/Satellite_Data/CHL"
filelist=$(/bin/ls ${datadir}/????/??/*-ACRI-L4-CHL-MULTI_4KM-GLO-REP.nc)
for file in ${filelist}
do
    outfile="${outdir}/subset_${file##/*/}"
    echo "extracting ${outfile}"
    ncks -O -d lon,2350,3110 -d lat,830,1500 ${file} ${outfile}
done

# KD490 daily data
datadir="/bali/data/ilima/Satellite_Data/Ocean_Color/KD490/daily"
outdir="/home/ivan/Data/Postproc/Satellite_Data/KD490"
filelist=$(/bin/ls ${datadir}/????/??/*-ACRI-L4-KD490-MULTI_4KM-GLO-REP.nc)
for file in ${filelist}
do
    outfile="${outdir}/subset_${file##/*/}"
    echo "extracting ${outfile}"
    ncks -O -d lon,2350,3110 -d lat,830,1500 ${file} ${outfile}
done
