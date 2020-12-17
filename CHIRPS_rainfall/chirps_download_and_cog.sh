#!/usr/bin/env bash

year=$1;
month=$2;
day=$3;

dea_filename="deafrica_chirps-v2.0_$year$month$day.tif";
echo $dea_filename;
    
if [ ! -f "$dea_filename" ]; then 

    # download and unzip
    filename="chirps-v2.0.$year.$month.$day.tif";

    if [ ! -f "$filename" ]; then
        url="https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_daily/tifs/p05/$year/$filename";
        wget $url;
        if [ "$?" != 0 ]; then
            url="$url.gz";
            wget $url;
            gunzip $filename.gz;
        fi;
        
        # fix nodata and metadata
        gdal_edit.py -a_nodata -9999. -mo unit=mm -mo source=$url $filename;
    fi;
    
rio cogeo create --overview-resampling average $filename $dea_filename;
fi;
