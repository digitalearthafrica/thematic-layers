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
        wget -q $url.gz;
        if [ "$?" != 0 ]; then
            wget -q $url;
        else
            gunzip $filename.gz;
        fi;
        
        # fix nodata and metadata
        gdal_edit.py -a_nodata -9999. -mo unit=mm -mo source=$url $filename;
    fi;
    
rio cogeo create -q --overview-resampling average $filename $dea_filename;
python ../generate_stac.py --product chirps_daily --platform chirps --band-name precipitation --datetime ${year}-${month}-${day}T12:00:00Z --url_root s3://deafrica-data-dev/chirps/${year}${month}${day} $dea_filename;

# put data in s3

fi;
