#!/bin/bash

# Subset PO.DAAC SST data to make data extraction at obs locations faster
# Created by Ivan Lima on Mon Feb  8 2021 10:55:08 -0500
# Time-stamp: <2021-02-08 11:13:28 ivan>

datadir="/bali/data/ilima/Satellite_Data/SST/PO.DAAC"
outdir="/home/ivan/Data/Postproc/PO.DAAC"
filelist=$(/bin/ls ${datadir}/????/???/*-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc)
for file in ${filelist}
do
    outfile="${outdir}/subset_${file##/*/}"
    echo "extracting ${outfile}"
    ncks -O -d lon,10000,12000 -d lat,11900,14000 ${file} ${outfile}
done
