from os.path import exists, basename
from datetime import datetime
import numpy as np
import shutil
import logging

import colored_logging as cl

from rasters import Raster
import rasters as rt

from .constants import L3T_ETAUX_SHORT_NAME, L3T_ETAUX_LONG_NAME
from .colors import RH_COLORMAP, WATER_COLORMAP, CLOUD_COLORMAP
from .L3TETAUX import L3TETAUX

logger = logging.getLogger(__name__)

def write_L3T_ETAUX(
            L3T_ETAUX_zip_filename: str,
            L3T_ETAUX_browse_filename: str,
            L3T_ETAUX_directory: str,
            orbit: int,
            scene: int,
            tile: str,
            time_UTC: datetime,
            build: str,
            product_counter: int,
            Ta_C: Raster,
            RH: Raster,
            Rn: Raster,
            Rg: Raster,
            SM: Raster,
            water_mask: Raster,
            cloud_mask: Raster,
            metadata: dict):
    L3T_ETAUX_granule = L3TETAUX(
        product_location=L3T_ETAUX_directory,
        orbit=orbit,
        scene=scene,
        tile=tile,
        time_UTC=time_UTC,
        build=build,
        process_count=product_counter
    )

    Ta_C.nodata = np.nan
    Ta_C = rt.where(water_mask, np.nan, Ta_C)
    Ta_C = Ta_C.astype(np.float32)

    RH.nodata = np.nan
    RH = rt.where(water_mask, np.nan, RH)
    RH = RH.astype(np.float32)

    Rn.nodata = np.nan
    Rn = rt.where(water_mask, np.nan, Rn)
    Rn = Rn.astype(np.float32)

    Rg.nodata = np.nan
    Rg = rt.where(water_mask, np.nan, Rg)
    Rg = Rg.astype(np.float32)

    SM.nodata = np.nan
    SM = rt.where(water_mask, np.nan, SM)
    SM = SM.astype(np.float32)

    water_mask = water_mask.astype(np.uint8)
    cloud_mask = cloud_mask.astype(np.uint8)

    L3T_ETAUX_granule.add_layer("Ta", Ta_C, cmap="jet")
    L3T_ETAUX_granule.add_layer("RH", RH, cmap=RH_COLORMAP)
    L3T_ETAUX_granule.add_layer("Rn", Rn, cmap="jet")
    L3T_ETAUX_granule.add_layer("Rg", Rg, cmap="jet")
    L3T_ETAUX_granule.add_layer("water", water_mask, cmap=WATER_COLORMAP)
    L3T_ETAUX_granule.add_layer("cloud", cloud_mask, cmap=CLOUD_COLORMAP)

    percent_good_quality = 100 * (1 - np.count_nonzero(np.isnan(Ta_C)) / Ta_C.size)
    metadata["ProductMetadata"]["QAPercentGoodQuality"] = percent_good_quality

    metadata["StandardMetadata"]["BuildID"] = build
    metadata["StandardMetadata"]["LocalGranuleID"] = basename(L3T_ETAUX_zip_filename)
    metadata["StandardMetadata"]["SISName"] = "Level 3/4 JET Product Specification Document"

    short_name = L3T_ETAUX_SHORT_NAME
    logger.info(f"L3T ETAUX short name: {cl.name(short_name)}")
    metadata["StandardMetadata"]["ShortName"] = short_name

    long_name = L3T_ETAUX_LONG_NAME
    logger.info(f"L3T ETAUX long name: {cl.name(long_name)}")
    metadata["StandardMetadata"]["LongName"] = long_name

    metadata["StandardMetadata"]["ProcessingLevelDescription"] = "Level 3 Tiled Evapotranspiration Auxiliary"

    L3T_ETAUX_granule.write_metadata(metadata)
    logger.info(f"writing L3T ETAUX product zip: {cl.file(L3T_ETAUX_zip_filename)}")
    L3T_ETAUX_granule.write_zip(L3T_ETAUX_zip_filename)
    logger.info(f"writing L3T ETAUX browse image: {cl.file(L3T_ETAUX_browse_filename)}")
    L3T_ETAUX_granule.write_browse_image(PNG_filename=L3T_ETAUX_browse_filename, cmap="jet")
    logger.info(f"removing L3T ETAUX tile granule directory: {cl.dir(L3T_ETAUX_directory)}")
    shutil.rmtree(L3T_ETAUX_directory)
