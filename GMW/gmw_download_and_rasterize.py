#!/usr/bin/env python


import geopandas as gpd
import os, sys
from rasterio.features import rasterize
from affine import Affine
import numpy as np
from datacube.utils.geometry import assign_crs
from datacube.utils.cog import write_cog
import xarray as xr
from shapely.geometry import box
import subprocess


def download_and_unzip_gmw(year):
    import requests
    import shutil
    from zipfile import ZipFile

    url = f'https://wcmc.io/GMW_{year}'
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True, allow_redirects=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    with ZipFile(local_filename) as z:
        z.extractall()
        shapename = [f for f in z.namelist() if f.endswith('.shp')][0]
    return shapename


def main(year, crs = 'EPSG:6933', res = 10):
    crs_code = crs.split(':')[1]
    dea_filename = f"deafrica_gmw_{year}_{crs_code}_{res}m.tif"
    if os.path.exists(dea_filename):
        print(f"{dea_filename} already exists")
        return

    # download extents if needed
    gmw_shp = f'GMW_001_GlobalMangroveWatch_{year}/01_Data/GMW_{year}_v2.shp'
    if not os.path.exists(gmw_shp):
        gmw_shp = download_and_unzip_gmw(year=year)

    # extract extents over Africa
    gmw = gpd.read_file(gmw_shp)

    deafrica_extent = gpd.read_file('../deafrica-extent/africa-extent.json')
    deafrica_extent = deafrica_extent.to_crs(gmw.crs)

    # find everything within deafrica_extent
    gmw_africa = gpd.sjoin(gmw, deafrica_extent,op='intersects')
    # include additional in the sqaure bounding box
    bound = box(*gmw_africa.total_bounds).buffer(0.001)
    deafrica_extent_square = gpd.GeoDataFrame(gpd.GeoSeries(bound), columns=['geometry'], crs=gmw_africa.crs)
    gmw_africa = gpd.sjoin(gmw, deafrica_extent_square,op='intersects')

    ## output raster setting
    gmw_africa = gmw_africa.to_crs(crs)
    bounds = gmw_africa.total_bounds
    bounds = np.hstack([np.floor(bounds[:2]/10)*10, np.ceil(bounds[2:]/10)*10])

    #transform = Affine(res, 0.0, bounds[0], 0.0, -1*res, bounds[3])
    out_shape = int((bounds[3]-bounds[1])/res), int((bounds[2]-bounds[0])/res)

    #rasterize in tiles
    tile_size = 50000
    ny = np.ceil(out_shape[0]/tile_size).astype(int)
    nx = np.ceil(out_shape[1]/tile_size).astype(int)

    for iy in np.arange(ny):
        for ix in np.arange(nx):
            y0 = bounds[3]-iy*tile_size*res
            x0 = bounds[0]+ix*tile_size*res
            y1 = np.max([bounds[1], bounds[3]-(iy+1)*tile_size*res])
            x1 = np.min([bounds[2], bounds[0]+(ix+1)*tile_size*res])
            
            transform = Affine(res, 0.0, x0, 0.0, -1*res, y0)  # pixel ul
            sub_shape = np.abs((y1-y0)/res).astype(int), np.abs((x1-x0)/res).astype(int)
        
            arr = rasterize(shapes=gmw_africa.geometry,
                            out_shape=sub_shape,
                            transform=transform,
                            fill=0,
                            all_touched=True,
                            default_value=1,
                            dtype=np.uint8)
            
            xarr = xr.DataArray(arr,
                                # pixel center
                                coords={'y':y0-np.arange(sub_shape[0])*res-res/2,
                                        'x':x0+np.arange(sub_shape[1])*res+res/2},
                                dims=('y','x'),
                                name='gmw')
        
            xarr = assign_crs(xarr, str(crs))
            write_cog(xarr, 
                      f'gmw_africa_{year}_{ix}_{iy}.tif',
                      overwrite=True)
            
    cmd = f"gdalbuildvrt gmw_africa_{year}.vrt gmw_africa_{year}_*_*.tif"
    r = subprocess.call(cmd, shell=True)
            
    cmd = f"rio cogeo create --overview-level 0 gmw_africa_{year}.vrt deafrica_gmw_{year}.tif"
    r = subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    if len(sys.argv)!=2:
        print("Select a year to download.")
    else:
        main(sys.argv[1])
        
