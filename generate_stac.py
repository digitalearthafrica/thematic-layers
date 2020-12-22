#!/usr/bin/env python

import click
import pathlib
import datetime
import json
import rasterio
from odc.index.stac import stac_transform
from pyproj import Transformer


from rio_cogeo.cogeo import cog_translate, cog_validate
from rio_cogeo.profiles import cog_profiles

def convert_to_cog(raster, out_path=None, validate=True, **kwargs):
    output_profile = cog_profiles.get("deflate")
    if out_path is None: out_path = str(raster.with_suffix(".tif")).replace(" ", "_")
    assert raster != out_path, "Can't convert to files of the same name"
    cog_translate(raster, out_path, output_profile, quiet=True, **kwargs)
    if validate:
        cog_validate(out_path)
    return pathlib.Path(out_path)


# this generally doesn't work
def get_datetime(raster):
    file_name = raster.stem
    date_string = file_name.split("_")[3]
    date = datetime.datetime.strptime(date_string, "%Y%m%d%H%M")
    return date.isoformat() + "Z"


def get_geometry(bbox, from_crs):
    transformer = Transformer.from_crs(from_crs, 4326)
    bbox_lonlat = [
        [bbox.left, bbox.bottom],
        [bbox.left, bbox.top],
        [bbox.right, bbox.top],
        [bbox.right, bbox.bottom],
        [bbox.left, bbox.bottom],
    ]
    geometry = {
        "type": "Polygon",
        "coordinates": [list(transformer.itransform(bbox_lonlat))],
    }
    return geometry, bbox_lonlat


def create_stac(raster, product, platform, band_name, date_string, path):
    transform = None
    shape = None
    crs = None

    with rasterio.open(raster) as dataset:
        transform = dataset.transform
        shape = dataset.shape
        crs = dataset.crs.to_epsg()
        bounds = dataset.bounds

    geometry, bbox = get_geometry(bounds, crs)
    stac_dict = {
        "id": raster.stem.replace(" ", "_"),
        "type": "Feature",
        "stac_version": "1.0.0-beta.2",
        "stac_extensions": [
            "proj"
        ],
        "properties": {"odc:product": product, "platform":platform, "datetime": date_string, "proj:epsg": crs},
        "bbox": bbox,
        "geometry": geometry,
        "links": [
            {
                "rel": "self",
                "href": pathlib.Path(path).joinpath(raster.with_suffix(".json")).as_posix()
            }
        ],
        "assets": {
            band_name: {
                "title": f"Data file for {band_name}",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                "roles": ["data"],
                "href": raster.stem + raster.suffix,
                "proj:shape": shape,
                "proj:transform": transform,
            }
        },
    }
    with open(raster.with_suffix(".json"), "w") as f:
        json.dump(stac_dict, f, indent=2)

    with open(raster.with_suffix(".odc-dataset.json"), "w") as f:
        json.dump(stac_transform(stac_dict), f, indent=2)

    return None

@click.command("create-odc-stac")
@click.option(
    "--product",
    type=str,
    required=True,
    help="ODC product name",
)
@click.option(
    "--platform",
    type=str,
    required=True,
    help="platform",
)
@click.option(
    "--band-name",
    type=str,
    required=True,
    help="Band name for the asset/measurement",
)
@click.option(
    "--datetime",
    default=None,
    type=str,
    help="A datetime for the file.",
)
@click.option(
    "--url_root",
    type=str,
    required=True,
    help="Root path for storage and access",
)
@click.argument("raster", type=str, nargs=1)
def cli(
    product,
    platform,
    band_name,
    datetime,
    url_root,
    raster
):
    create_stac(pathlib.Path(raster), product, platform, band_name, datetime, url_root)


if __name__ == "__main__":
    cli()



