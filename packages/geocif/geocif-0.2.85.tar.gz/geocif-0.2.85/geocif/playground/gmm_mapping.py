"""
winter_crop_mapping.py (v2)

Adds a **Gaussian Mixture Model (GMM)** step (2‑component, unsupervised) to separate winter crops
from other cropland based on early‑spring NDVI.  All processing still runs in Python + Earth
Engine; only the probabilistic GMM fitting happens client‑side using scikit‑learn.

-------------------------------------------------------------
Quick usage (identical entry‑point):

    from winter_crop_mapping import generate_winter_crop
    ic = generate_winter_crop('Ukraine', use_gmm=True)

See README in docstring for explanations.
"""
from typing import Optional, Dict
import math
import ee
import numpy as np

import rasterio
from pathlib import Path
dir = Path(r'D:\Users\ritvik\projects\GEOGLAM\Input\Global_Datasets\Masks')

# Open Percent_Winter_Wheat.tif using rasterio
with rasterio.open(dir / 'Percent_Winter_Wheat.tif') as src:
    percent_winter_wheat = src.read(1)  # Read the first band
    profile = src.profile  # Get the metadata profile
    breakpoint()

ee.Initialize(project='ee-rit')
from sklearn.mixture import GaussianMixture
# ------------------------------------------------------------------
# Country geometry & auxiliary layers
# ------------------------------------------------------------------

def get_country_geometry(name: str) -> ee.Geometry:
    fc = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017')
    feat = fc.filter(ee.Filter.eq('country_na', name))
    if feat.size().getInfo() == 0:
        raise ValueError(f'Country {name} not found.')
    return feat.geometry()


def cropland_mask() -> ee.Image:
    wc = ee.ImageCollection('ESA/WorldCover/v200').first().select('Map')
    return wc.eq(40).selfMask().rename('cropland')

CROPLAND = cropland_mask()

# ------------------------------------------------------------------
# Helper ‑ Gaussian PDF as EE expression
# ------------------------------------------------------------------

def gaussian_pdf(x: ee.Image, mu: float, sigma: float) -> ee.Image:
    return x.subtract(mu).pow(2).divide(-2 * sigma ** 2).exp().divide(sigma * math.sqrt(2 * math.pi))

# ------------------------------------------------------------------
# Core per‑year processor
# ------------------------------------------------------------------

def gmm_params(samples: np.ndarray, year: int) -> Dict[str, float]:
    gmm = GaussianMixture(n_components=2, random_state=year)
    gmm.fit(samples.reshape(-1, 1))
    means = gmm.means_.flatten()
    sigmas = np.sqrt(gmm.covariances_.flatten())
    weights = gmm.weights_.flatten()
    # winter crop component assumed to have higher mean NDVI in early spring
    idx_winter = np.argmax(means)
    idx_other = 1 - idx_winter
    return {
        'w1': float(weights[idx_winter]), 'mu1': float(means[idx_winter]), 'sigma1': float(sigmas[idx_winter]),
        'w2': float(weights[idx_other]),  'mu2': float(means[idx_other]),  'sigma2': float(sigmas[idx_other])
    }


def winter_crop_for_year(year: int, region: ee.Geometry, use_gmm: bool = False) -> ee.Image:
    start = ee.Date.fromYMD(year, 1, 1)
    end = ee.Date.fromYMD(year, 4, 30)

    ndvi_scale = 0.0001
    ndvi = (ee.ImageCollection('MODIS/061/MOD13Q1')
            .filterDate(start, end)
            .select('NDVI')
            .max()
            .multiply(ndvi_scale)  # real NDVI 0‑1
            .rename('NDVI'))

    if use_gmm:
        # ----------------------------------------------------
        # 1. Sample NDVI values on cropland
        # ----------------------------------------------------
        sample_fc = (ndvi.updateMask(CROPLAND)
                       .sample(region=region, scale=250, numPixels=5000, seed=year, geometries=False))
        ndvi_vals = np.array(sample_fc.aggregate_array('NDVI').getInfo(), dtype=float)
        params = gmm_params(ndvi_vals, year)

        # ----------------------------------------------------
        # 2. Compute per‑pixel winter probability using closed‑form GMM equation
        # ----------------------------------------------------
        pdf1 = gaussian_pdf(ndvi, params['mu1'], params['sigma1']).multiply(params['w1'])
        pdf2 = gaussian_pdf(ndvi, params['mu2'], params['sigma2']).multiply(params['w2'])
        winter_prob = pdf1.divide(pdf1.add(pdf2)).rename('winter_prob')
        winter_crop = winter_prob.gt(0.5).And(CROPLAND).rename('winter_crop').uint8()
    else:
        winter_crop = ndvi.gt(0.3).And(CROPLAND).rename('winter_crop').uint8()
        winter_prob = winter_crop.float()  # dummy if no GMM, keeps band alignment

    winter_crop = winter_crop.clip(region)

    # 5 km aggregation of winter_crop mask
    winter_frac = (winter_crop
                   .reduceResolution(reducer=ee.Reducer.mean(), maxPixels=1024)
                   .reproject(crs='EPSG:4326', scale=5000)
                   .rename('winter_frac'))

    return (ee.Image.cat([winter_crop, winter_frac, winter_prob])
            .set({'year': year, 'system:time_start': start.millis()}))

# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def generate_winter_crop(country_name: str,
                         start_year: int = 2001,
                         end_year: int = 2024,
                         use_gmm: bool = True,
                         out_asset: Optional[str] = None) -> ee.ImageCollection:
    region = get_country_geometry(country_name)
    years = list(range(start_year, end_year + 1))
    ic = ee.ImageCollection([winter_crop_for_year(y, region, use_gmm) for y in years])

    if out_asset:
        export = ic.toBands().clip(region)
        task = ee.batch.Export.image.toAsset(
            image=export,
            description=f'winter_crop_{country_name}_{start_year}_{end_year}',
            assetId=out_asset,
            region=region,
            scale=250,
            maxPixels=1e13,
            pyramidingPolicy={'.default': 'mode'}
        )
        task.start()
        print('Export task started:', task.id)

    return ic
