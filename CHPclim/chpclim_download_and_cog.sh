#!/usr/bin/env bash

for month in {01..12}; do
    dea_filename="dea_chpclim_50n_50s_$month.tif";
    echo $dea_filename;
    
    if [ ! -f "$dea_filename" ]; then 
	# download and unzip
	filename="chpclim.$month.tif";

	if [ ! -f "$filename" ]; then
	    url="https://data.chc.ucsb.edu/products/CHPclim/50N-50S.with_oceans/monthly/$filename.gz";
	    wget $url;
	    gunzip $filename.gz;
	    # fix nodata and metadata
	    gdal_edit.py -a_nodata -9999. -mo unit=mm -mo source=$url $filename;
	fi;
	
	#unzip $filename;
	rio cogeo create --overview-resampling average $filename $deafrica_filename;
    fi;
done;
