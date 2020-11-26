#!/usr/bin/env python

import geopandas as gpd
import subprocess
import os


# download tile grid if not already exists
if not os.path.exists('UTM_land.shp'):
    subprocess.call('wget https://ghsl.jrc.ec.europa.eu/documents/GHS_BUILT_S2comp2018_GLOBE_R2020A_tile_schema.zip?t=1603983376', shell=True)
    subprocess.call('unzip GHS_BUILT_S2comp2018_GLOBE_R2020A_tile_schema.zip', shell=True)
    
tiles = gpd.read_file('UTM_land.shp')

deafrica_extent = gpd.read_file('https://github.com/digitalearthafrica/deafrica-extent/raw/master/africa-extent.json')

grids = tiles[tiles.intersects(deafrica_extent.loc[0].geometry)].grid_zone.values

# 95 grids
for grid in grids:

    grid_file = f'{grid}_PROB.tif'
    if not os.path.exists(grid_file):
        url = f'https://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_S2comp2018_GLOBE_R2020A/GHS_BUILT_S2comp2018_GLOBE_R2020A_UTM_10/V1-0/{grid_file}'
        subprocess.call(f'wget {url}', shell=True)


africa-extent-bbox.json
