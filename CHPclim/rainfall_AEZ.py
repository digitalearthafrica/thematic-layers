

import sys
import xarray as xr
import geopandas as gpd
from rasterio.features import rasterize
from affine import Affine
import numpy as np
from matplotlib import pyplot as plt

#aez_name = 'Western'

# requires shapefiles for AEZ

def main(aez_name):
    aez = gpd.read_file(f'../../simplified_AEZs/{aez_name}.shp')
    bounds = aez.iloc[0].geometry.bounds
    
    months = np.arange(1,13)
    total_precip = np.zeros(len(months))
    
    for i, mon in enumerate(months):
        clim = f"deafrica_chpclim_50n_50s_{mon:02d}.tif"
        img_all = xr.open_rasterio(clim, chunks=dict(x=1000,y=1000)).squeeze('band')
        img = img_all.sel(x=slice(bounds[0], bounds[2]), y=slice(bounds[3],bounds[1]))

        res = img.x.values[1]-img.x.values[0]
        transform = Affine(res, 0.0, img.x.values[0], 0.0, -1*res, img.y.values[0])
        out_shape = len(img.y), len(img.x)
        
        arr = rasterize(shapes=aez.geometry,
                        out_shape=out_shape,
                        transform=transform,
                        fill=0,
                        all_touched=True,
                        default_value=1,
                        dtype=np.uint8)
        
        total_precip[i] = img.where(arr>0).mean().values

    plt.bar(months, total_precip)
    plt.xlabel('Month')
    plt.ylabel('Average precipitation (mm)')
    plt.title(aez_name)
    plt.savefig(f'{aez_name}_clim.png')


if __name__ == "__main__":
    if len(sys.argv)!=2:
        print("Select a AEZ (e.g. Northern, Sahel, Western, Central, Eastern, Southern or Indian_ocean)")
    else:
        main(sys.argv[1])
