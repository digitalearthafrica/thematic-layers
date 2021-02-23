#!/usr/bin/env python

import sys
sys.path.append("..") 

import requests
import os
import zipfile
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles


output_profile = cog_profiles.get("deflate")


def download_and_cog(year, month, day):
    dea_filename = f"deafrica_chirps-v2.0_{year}{month}{day}.tif"
    
    filename = f"chirps-v2.0.{year}.{month}.{day}.tif"
    # download and unzip
    if not os.path.exists(filename):
        url = f"https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_daily/tifs/p05/{year}/{filename}"
        r = requests.get(url)
        if r!=200:
            r = request.get(url+'.gz')
            if r!=200: return
            with zipfile(filename+'.gz') as zp:
                zp.extractall()
    # cog
    cog_translate(raster, out_path, output_profile, nodata=-9999, overview_resampling='average' quiet=True)

    
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
