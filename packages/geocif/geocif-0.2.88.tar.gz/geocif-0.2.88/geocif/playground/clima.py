#!/usr/bin/env python3
"""
Download ISIMIP3b derived maize yield data and compute yield anomalies as CLIMADA hazard
Author: Your Name
Date: 2024
"""

import os
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
import requests
from isimip_client.client import ISIMIPClient
from climada import CONFIG
from climada.hazard import Hazard
from climada.entity import ImpactFuncSet, ImpactFunc
from climada.engine import Impact
from climada_petals.hazard.relative_cropyield import RelativeCropyield
from climada_petals.entity.exposures.crop_production import CropProduction

# ============================================================================
# 1. SETUP AND CONFIGURATION
# ============================================================================

# Define working directories
BASE_DIR = CONFIG.local_data.save_dir.dir() / "ISIMIP3b_maize_analysis"
DOWNLOAD_DIR = BASE_DIR / "downloads"
OUTPUT_DIR = BASE_DIR / "output"
FIGURES_DIR = BASE_DIR / "figures"

# Create directories
for dir_path in [DOWNLOAD_DIR, OUTPUT_DIR, FIGURES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Analysis parameters
CROP = 'mai'  # maize
BBOX = None  # Set to None for global, or define as [lon_min, lat_min, lon_max, lat_max]
REFERENCE_PERIOD = (1985, 2014)  # Reference period for anomaly calculation

# ============================================================================
# 2. SEARCH AND DOWNLOAD ISIMIP3b DERIVED YIELD DATA
# ============================================================================

def search_isimip3b_yield_data(crop='mai', search_absolute_yield=False):
    """
    Search for ISIMIP3b derived yield data
    """
    client = ISIMIPClient()
    
    print(f"\nSearching for ISIMIP3b {crop} yield data...")
    
    # Try different search strategies based on what type of data we want
    if search_absolute_yield:
        # Search for absolute yield data
        search_terms = [
            f'ISIMIP3b yield {crop}',
            f'ISIMIP3b {crop} yield t/ha',
            f'ISIMIP3b OutputData agriculture {crop}',
            f'ISIMIP3b agriculture {crop}'
        ]
    else:
        # Search for yield change data (which is what we found)
        search_terms = [
            f'ISIMIP3b yieldchange {crop}',
            f'yieldchange-{crop}',
            f'ISIMIP3b DerivedOutputData {crop}'
        ]
    
    all_datasets = {'results': [], 'count': 0}
    
    for term in search_terms:
        print(f"  Trying: {term}")
        datasets = client.datasets(query=term)
        
        if datasets.get('count', 0) > 0:
            # Filter for ISIMIP3b only
            for ds in datasets.get('results', []):
                if 'ISIMIP3b' in ds.get('path', '') or ds.get('specifiers', {}).get('simulation_round') == 'ISIMIP3b':
                    # Avoid duplicates
                    if ds['id'] not in [d['id'] for d in all_datasets['results']]:
                        all_datasets['results'].append(ds)
            all_datasets['count'] = len(all_datasets['results'])
    
    # If no results, try broader search
    if all_datasets['count'] == 0:
        print("  No results with specific searches, trying broader search...")
        datasets = client.datasets(
            simulation_round='ISIMIP3b',
            query=crop
        )
        all_datasets = datasets
    
    # Also try searching for any agricultural data in ISIMIP3b
    print("\n  Also searching for general ISIMIP3b agricultural data...")
    ag_datasets = client.datasets(
        simulation_round='ISIMIP3b',
        sector='agriculture'
    )
    print(f"  Found {ag_datasets.get('count', 0)} agricultural datasets in ISIMIP3b")
    
    if ag_datasets.get('count', 0) > 0:
        print("\n  Sample agricultural datasets available:")
        for i, ds in enumerate(ag_datasets.get('results', [])[:5]):
            print(f"    {i+1}. {ds.get('name', 'Unknown')}")
            # Check if this dataset has files
            try:
                files = client.files(dataset=ds['id'])
                print(f"       Files: {files.get('count', 0)}")
            except:
                print(f"       Files: Unable to check")
    
    return all_datasets

def download_file_by_id(file_id, download_dir):
    """
    Download a specific file using its ISIMIP file ID
    """
    # Construct the direct download URL
    file_url = f"https://data.isimip.org/files/{file_id}/"
    
    print(f"\nAttempting to download file ID: {file_id}")
    print(f"URL: {file_url}")
    
    try:
        # First, get file metadata
        response = requests.get(file_url)
        response.raise_for_status()
        
        # The response might contain metadata about the file
        # Try to extract the actual file URL from the response
        # ISIMIP might redirect or provide a download link
        
        # Look for actual file URL in response
        if 'files.isimip.org' in response.text:
            import re
            # Try to find the actual file URL
            matches = re.findall(r'https://files\.isimip\.org/[^"\'<>\s]+\.nc\d?', response.text)
            if matches:
                actual_file_url = matches[0]
                print(f"Found actual file URL: {actual_file_url}")
                
                # Extract filename from URL
                filename = actual_file_url.split('/')[-1]
                local_path = download_dir / filename
                
                if local_path.exists():
                    print(f"File already exists: {local_path}")
                    return local_path
                
                # Download the actual file
                print(f"Downloading to: {local_path}")
                file_response = requests.get(actual_file_url, stream=True)
                file_response.raise_for_status()
                
                total_size = int(file_response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(local_path, 'wb') as f:
                    for chunk in file_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"\rProgress: {percent:.1f}%", end='')
                
                print(f"\nSuccessfully downloaded: {local_path}")
                return local_path
        
        # If we can't find the file URL, save the response for debugging
        print("Could not find direct file URL in response")
        print("Response preview:", response.text[:500])
        
    except Exception as e:
        print(f"Error downloading file: {e}")
    
    return None


def get_isimip3b_file_ids():
    """
    Return known ISIMIP3b file IDs for maize yield data
    Based on the working example provided
    """
    # Add the working file ID you found
    known_file_ids = [
        '9afab06d-99c6-4d22-993e-0d67233f965b',  # The one that works
        'fd28621c-72d9-4bb3-ba09-61bcf6f9af38',  # acea_mri-esm2-0_w5e5_ssp126
        '87987feb-6c97-497d-91a5-db1e75887d4f',  # acea_mri-esm2-0_w5e5_ssp585
        'bb82fab7-3f3d-465a-9458-ed5c3cbb16da',  # acea_mri-esm2-0_w5e5_historical
        'b71415dc-e3d3-4045-ba71-e8289c75d1c6',  # acea_ukesm1-0-ll_w5e5_ssp126
        'de7bd62d-d8b0-44ad-915c-3e6039e553da',  # acea_ukesm1-0-ll_w5e5_ssp585
        'a3df6abd-0b05-47b6-8e15-b0649b914de5',  # acea_ukesm1-0-ll_w5e5_historical
        '13b1a1fe-6bec-4b2d-abc8-bed8c4a7b85e',  # crover_gfdl-esm4_w5e5_ssp126
        '61060b52-3e69-4233-8c8e-616ea0141522',  # crover_gfdl-esm4_w5e5_ssp585
        '19ba3056-6905-4645-8440-30b5503d411c',  # crover_gfdl-esm4_w5e5_historical
    ]
    
    # You can also search for file IDs programmatically
    client = ISIMIPClient()
    
    print("\nSearching for ISIMIP3b maize yield file IDs...")
    
    # Try to get files directly
    try:
        # Search for all files with maize in the name
        files = client.files(query='yieldchange-mai ISIMIP3b')
        
        if files.get('count', 0) > 0:
            print(f"Found {files['count']} files")
            file_ids = []
            for f in files.get('results', [])[:10]:  # First 10
                file_id = f.get('id')
                if file_id:
                    file_ids.append(file_id)
                    print(f"  - {f.get('name', 'Unknown')}: {file_id}")
            return known_file_ids + file_ids
    except Exception as e:
        print(f"Error searching for files: {e}")
    
    return known_file_ids

def download_yield_files(datasets, download_dir, include_all_scenarios=False):
    """
    Download yield files from ISIMIP
    """
    downloaded_files = []
    client = ISIMIPClient()
    
    print("\n" + "="*80)
    print("DOWNLOAD DETAILS")
    print("="*80)
    
    for dataset in datasets['results']:
        dataset_name = dataset.get('name', '')
        dataset_id = dataset.get('id', '')
        
        print(f"\nDataset: {dataset_name}")
        print(f"Dataset ID: {dataset_id}")
        
        # Check if it's historical data (unless we want all scenarios)
        if not include_all_scenarios:
            if 'historical' not in dataset_name.lower():
                if dataset.get('specifiers', {}).get('climate_scenario') != 'historical':
                    print("  -> Skipping non-historical scenario")
                    continue
        
        # Print dataset metadata URL
        metadata_url = dataset.get('metadata_url', '')
        if metadata_url:
            print(f"  Metadata URL: {metadata_url}")
        
        # Get files for this dataset
        print(f"  Fetching file list from API...")
        try:
            files = client.files(dataset=dataset_id)
            print(f"  -> Found {files.get('count', 0)} files in this dataset")
        except Exception as e:
            print(f"  -> Error getting files: {e}")
            continue
        
        if files.get('count', 0) == 0:
            print(f"  -> No files found for this dataset")
            continue
            
        for i, file_info in enumerate(files['results']):
            print(f"\n  File {i+1}/{files['count']}:")
            
            # Print all available file information
            filename = file_info.get('name', 'unknown.nc')
            file_path = file_info.get('path', '')
            file_size = file_info.get('size', 0)
            
            print(f"    Filename: {filename}")
            print(f"    Path: {file_path}")
            print(f"    Size: {file_size / 1024 / 1024:.2f} MB" if file_size else "    Size: Unknown")
            
            # Get file URL - try different possible keys
            file_url = file_info.get('file_url') or file_info.get('url')
            
            # If no direct URL, try constructing from path
            if not file_url and file_path:
                # Try different URL patterns
                possible_urls = [
                    f"https://files.isimip.org/{file_path}",
                    f"https://data.isimip.org/{file_path}",
                    f"https://www.isimip.org/files/{file_path}"
                ]
                print("    No direct URL found, trying constructed URLs:")
                for url in possible_urls:
                    print(f"      - {url}")
                file_url = possible_urls[0]  # Try the first one
            
            local_path = download_dir / filename
            
            # Skip if already downloaded
            if local_path.exists():
                print(f"    -> File already exists locally: {local_path}")
                downloaded_files.append(local_path)
                continue
            
            # Download file
            if file_url:
                print(f"    Attempting download from: {file_url}")
                print(f"    Target location: {local_path}")
                
                try:
                    print("    -> Sending request...")
                    response = requests.get(file_url, stream=True, timeout=30)
                    
                    print(f"    -> Response status: {response.status_code}")
                    response.raise_for_status()
                    
                    total_size = int(response.headers.get('content-length', 0))
                    if total_size:
                        print(f"    -> Download size: {total_size / 1024 / 1024:.2f} MB")
                    
                    downloaded = 0
                    
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    percent = (downloaded / total_size) * 100
                                    print(f"\r    -> Progress: {percent:.1f}%", end='')
                    
                    print(f"\n    -> Successfully saved to: {local_path}")
                    downloaded_files.append(local_path)
                    
                except requests.exceptions.RequestException as e:
                    print(f"    -> Download failed: {type(e).__name__}: {e}")
                    if hasattr(e, 'response') and e.response is not None:
                        print(f"    -> Response content: {e.response.text[:500]}")
                    if local_path.exists():
                        local_path.unlink()  # Remove partial download
                        print(f"    -> Removed partial download")
                        
                except Exception as e:
                    print(f"    -> Unexpected error: {type(e).__name__}: {e}")
                    if local_path.exists():
                        local_path.unlink()
            else:
                print(f"    -> No URL available for this file")
                print(f"    -> Available file info keys: {list(file_info.keys())}")
    
    print("\n" + "="*80)
    print(f"DOWNLOAD SUMMARY: {len(downloaded_files)} files downloaded successfully")
    print("="*80 + "\n")
    
    return downloaded_files

# ============================================================================
# 3. PROCESS YIELD DATA AND COMPUTE ANOMALIES (FIXED VERSION)
# ============================================================================

def process_yield_data(nc_file, bbox=None):
    """
    Process NetCDF yield data and prepare for anomaly calculation
    """
    print(f"\nProcessing: {nc_file.name}")
    
    # Open NetCDF file with decode_times=False to avoid the time decoding error
    try:
        ds = xr.open_dataset(nc_file, decode_times=False)
        print("Opened dataset with decode_times=False")
    except Exception as e:
        print(f"Error opening dataset: {e}")
        raise
    
    print("Dataset variables:", list(ds.variables))
    print("Dataset dimensions:", dict(ds.dims))
    
    # For yieldchange data, the variable might be named differently
    yield_vars = []
    
    # Check for various possible variable names
    possible_names = ['yieldchange-mai', 'yieldchange_mai', 'yield-mai', 'yield_mai', 
                      'mai', 'yield', 'yieldchange', 'crop_yield']
    
    for var in ds.variables:
        if any(name in var.lower() for name in ['yield', 'mai']):
            yield_vars.append(var)
    
    # If no yield variables found, look for the main data variable
    if not yield_vars:
        data_vars = [v for v in ds.data_vars if v not in ['lat', 'lon', 'time', 'latitude', 'longitude']]
        if data_vars:
            yield_vars = [data_vars[0]]
    
    if not yield_vars:
        raise ValueError(f"No yield variable found in {nc_file}. Variables: {list(ds.variables)}")
    
    yield_var = yield_vars[0]
    print(f"Using yield variable: {yield_var}")
    
    # Extract yield data
    yield_data = ds[yield_var]
    
    # Handle the time coordinate manually
    if 'time' in ds.variables:
        time_var = ds['time']
        print(f"Time variable attributes: {time_var.attrs}")
        
        # Check if time units indicate years
        time_units = time_var.attrs.get('units', '')
        if 'years since' in time_units:
            # Extract the reference year
            import re
            match = re.search(r'years since (\d{4})', time_units)
            if match:
                ref_year = int(match.group(1))
                # Convert time values to actual years
                years = ref_year + time_var.values
                print(f"Converted time from '{time_units}' to years: {years[0]} - {years[-1]}")
                
                # Create new time coordinate with proper years
                yield_data = yield_data.assign_coords(time=years)
            else:
                print("Warning: Could not parse reference year from time units")
        else:
            print(f"Time units: {time_units}")
    
    # Check if it's historical data and adjust time range if needed
    if 'time' in yield_data.coords:
        time_range = yield_data.time.values
        print(f"Time range: {time_range[0]} to {time_range[-1]}")
        
        # If time values are very large (like ordinal days), convert them
        if hasattr(time_range[0], '__iter__') == False and time_range[0] > 2100:
            # Assume these are years since some epoch, try to convert
            if time_range[0] > 100000:  # Very large numbers, might be days
                # This is a fallback - you might need to adjust based on your specific data
                print("Warning: Time values seem to be in unexpected format")
    
    # Check if this is yield change data (relative to baseline)
    # If so, we might need to handle it differently
    if 'yieldchange' in yield_var.lower():
        print("  Note: This appears to be yield change data (not absolute yields)")
        # Yield change data is often already expressed as anomalies
        # We might need to adjust our processing
    
    # Standardize dimension names
    if 'latitude' in yield_data.dims:
        yield_data = yield_data.rename({'latitude': 'lat'})
    if 'longitude' in yield_data.dims:
        yield_data = yield_data.rename({'longitude': 'lon'})
    
    # Apply bounding box if specified
    if bbox:
        lon_min, lat_min, lon_max, lat_max = bbox
        yield_data = yield_data.sel(
            lon=slice(lon_min, lon_max),
            lat=slice(lat_min, lat_max)
        )
    
    return yield_data, ds

def compute_yield_anomaly(yield_data, reference_period):
    """
    Compute yield anomaly relative to reference period
    """
    print(f"\nComputing anomalies relative to {reference_period}")
    
    # Get time coordinate name
    time_dim = 'time' if 'time' in yield_data.dims else 'year'
    
    # Check time coordinate values
    time_values = yield_data[time_dim].values
    print(f"Time values range: {time_values[0]} to {time_values[-1]}")
    print(f"Time values type: {type(time_values[0])}")
    
    # Handle different time formats
    if hasattr(time_values[0], 'year'):
        # If time values are datetime objects
        years = [t.year for t in time_values]
        time_coord = xr.DataArray(years, dims=[time_dim])
        yield_data = yield_data.assign_coords({time_dim: time_coord})
    elif isinstance(time_values[0], (int, float, np.integer, np.floating)):
        # If time values are already years or can be converted
        if time_values[0] > 1800 and time_values[0] < 2200:
            # Already looks like years
            years = time_values.astype(int)
        else:
            # Might need conversion - this is dataset specific
            print("Warning: Time values don't look like years, using as-is")
            years = time_values
        
        time_coord = xr.DataArray(years, dims=[time_dim])
        yield_data = yield_data.assign_coords({time_dim: time_coord})
    
    # Filter data for reference period
    try:
        ref_start, ref_end = reference_period
        
        # Select reference period data
        if hasattr(yield_data[time_dim].values[0], '__iter__') == False:
            # Simple numeric selection
            ref_mask = (yield_data[time_dim] >= ref_start) & (yield_data[time_dim] <= ref_end)
            ref_data = yield_data.where(ref_mask, drop=True)
        else:
            # Use slice selection
            ref_data = yield_data.sel({time_dim: slice(ref_start, ref_end)})
        
        if len(ref_data[time_dim]) == 0:
            print(f"Warning: No data found in reference period {reference_period}")
            print(f"Available time range: {yield_data[time_dim].min().values} to {yield_data[time_dim].max().values}")
            # Use first 30 years as reference instead
            ref_data = yield_data.isel({time_dim: slice(0, min(30, len(yield_data[time_dim])))})
            print(f"Using first {len(ref_data[time_dim])} years as reference period")
        
        ref_mean = ref_data.mean(dim=time_dim)
        ref_std = ref_data.std(dim=time_dim)
        
        print(f"Reference period: {len(ref_data[time_dim])} years")
        print(f"Reference mean range: {float(ref_mean.min().compute()):.3f} to {float(ref_mean.max().compute()):.3f}")
        
    except Exception as e:
        print(f"Error computing reference statistics: {e}")
        # Fallback: use entire time series
        ref_mean = yield_data.mean(dim=time_dim)
        ref_std = yield_data.std(dim=time_dim)
        print("Using entire time series for reference statistics")
    
    # Compute relative anomaly (as fraction of mean)
    # anomaly = (yield - mean) / mean
    anomaly_relative = (yield_data - ref_mean) / ref_mean
    anomaly_relative = anomaly_relative.where(ref_mean != 0)  # Avoid division by zero
    
    # Compute standardized anomaly (z-score)
    # anomaly = (yield - mean) / std
    anomaly_zscore = (yield_data - ref_mean) / ref_std
    anomaly_zscore = anomaly_zscore.where(ref_std != 0)
    
    return {
        'relative': anomaly_relative,
        'zscore': anomaly_zscore,
        'ref_mean': ref_mean,
        'ref_std': ref_std,
        'absolute': yield_data
    }

# ============================================================================
# 4. CREATE CLIMADA HAZARD FROM YIELD ANOMALIES
# ============================================================================

def create_anomaly_hazard(anomaly_data, hazard_type='relative'):
    """
    Create CLIMADA hazard from yield anomaly data
    
    Parameters:
    -----------
    anomaly_data : dict
        Dictionary with 'relative' and 'zscore' anomaly xarray DataArrays
    hazard_type : str
        Type of anomaly to use: 'relative' or 'zscore'
    """
    print(f"\nCreating CLIMADA hazard from {hazard_type} anomalies")
    
    # Get the anomaly data
    data = anomaly_data[hazard_type]
    
    # Get dimensions
    time_dim = 'time' if 'time' in data.dims else 'year'
    times = data[time_dim].values
    lats = data.lat.values
    lons = data.lon.values
    
    # Create mesh grid
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    
    # Flatten spatial coordinates
    centroids_lat = lat_grid.flatten()
    centroids_lon = lon_grid.flatten()
    n_centroids = len(centroids_lat)
    
    # Create hazard
    haz = Hazard('YieldAnomaly')
    
    # Set centroids
    from climada.hazard import Centroids
    haz.centroids = Centroids()
    haz.centroids.set_lat_lon(centroids_lat, centroids_lon)
    
    # Set events (one per year)
    n_events = len(times)
    haz.event_id = np.arange(1, n_events + 1)
    haz.event_name = [str(int(t)) if isinstance(t, (int, np.integer)) 
                      else pd.Timestamp(t).strftime('%Y') 
                      for t in times]
    haz.date = np.array([pd.Timestamp(f'{int(t)}-01-01').toordinal() if isinstance(t, (int, np.integer))
                         else pd.Timestamp(t).toordinal() 
                         for t in times])
    haz.orig = np.ones(n_events) * False  # All are modeled events
    
    # Set frequency (annual events)
    haz.frequency = np.ones(n_events) / n_events
    
    # Set intensity matrix (sparse)
    from scipy import sparse
    intensity_matrix = []
    
    for i, t in enumerate(times):
        # Get data for this time
        if isinstance(t, (int, np.integer)):
            time_data = data.sel({time_dim: t})
        else:
            time_data = data.sel({time_dim: t}, method='nearest')
        
        # Flatten and handle NaN values
        intensity = time_data.values.flatten()
        
        # Create sparse row (only non-zero and non-NaN values)
        valid_mask = ~np.isnan(intensity) & (intensity != 0)
        if valid_mask.any():
            row = sparse.csr_matrix((intensity[valid_mask], 
                                   (np.zeros(valid_mask.sum()), 
                                    np.where(valid_mask)[0])), 
                                   shape=(1, n_centroids))
            intensity_matrix.append(row)
        else:
            # Empty row if all NaN or zero
            intensity_matrix.append(sparse.csr_matrix((1, n_centroids)))
    
    # Stack all events
    haz.intensity = sparse.vstack(intensity_matrix)
    
    # Set fraction matrix (all areas affected where there's data)
    haz.fraction = haz.intensity.copy()
    haz.fraction.data = np.ones_like(haz.fraction.data)
    
    # Set units and other attributes
    if hazard_type == 'relative':
        haz.units = 'fraction'
        haz.intensity_def = 'Relative yield anomaly'
    else:
        haz.units = 'z-score'
        haz.intensity_def = 'Standardized yield anomaly'
    
    # Check hazard
    haz.check()
    
    return haz

# ============================================================================
# 5. VISUALIZATION FUNCTIONS
# ============================================================================

def plot_yield_analysis(anomaly_data, output_dir):
    """
    Create comprehensive plots of yield analysis
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Get time dimension
    data = anomaly_data['absolute']
    time_dim = 'time' if 'time' in data.dims else 'year'
    
    # 1. Mean yield map
    ax = axes[0, 0]
    ref_mean = anomaly_data['ref_mean']
    im1 = ax.pcolormesh(ref_mean.lon, ref_mean.lat, ref_mean, 
                        cmap='YlGn', shading='auto')
    ax.set_title('Mean Yield (Reference Period)')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.colorbar(im1, ax=ax, label='Yield [t/ha]')
    
    # 2. Coefficient of variation
    ax = axes[0, 1]
    cv = anomaly_data['ref_std'] / anomaly_data['ref_mean']
    cv = cv.where(anomaly_data['ref_mean'] > 0)
    im2 = ax.pcolormesh(cv.lon, cv.lat, cv, 
                        cmap='RdYlBu_r', shading='auto', vmin=0, vmax=1)
    ax.set_title('Coefficient of Variation')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.colorbar(im2, ax=ax, label='CV')
    
    # 3. Time series of global mean
    ax = axes[1, 0]
    global_mean = data.mean(dim=['lat', 'lon'])
    global_mean.plot(ax=ax, label='Global mean')
    ax.set_title('Global Mean Yield Time Series')
    ax.set_xlabel('Year')
    ax.set_ylabel('Yield [t/ha]')
    ax.grid(True, alpha=0.3)
    
    # 4. Anomaly distribution
    ax = axes[1, 1]
    relative_anomaly = anomaly_data['relative']
    # Flatten all anomalies
    all_anomalies = relative_anomaly.values.flatten()
    all_anomalies = all_anomalies[~np.isnan(all_anomalies)]
    
    ax.hist(all_anomalies, bins=50, density=True, alpha=0.7, edgecolor='black')
    ax.axvline(x=0, color='red', linestyle='--', label='Zero anomaly')
    ax.set_xlabel('Relative Anomaly')
    ax.set_ylabel('Density')
    ax.set_title('Distribution of Yield Anomalies')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'yield_analysis_overview.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Additional plot: Extreme years
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Find years with largest positive and negative anomalies
    global_anomaly = relative_anomaly.mean(dim=['lat', 'lon'])
    sorted_years = global_anomaly.sortby(global_anomaly)
    
    # Plot worst and best years
    worst_year = sorted_years[time_dim].values[0]
    best_year = sorted_years[time_dim].values[-1]
    
    # Worst year
    ax = axes[0, 0]
    worst_data = relative_anomaly.sel({time_dim: worst_year}, method='nearest')
    im = ax.pcolormesh(worst_data.lon, worst_data.lat, worst_data,
                       cmap='RdBu', shading='auto', vmin=-0.5, vmax=0.5)
    ax.set_title(f'Worst Year: {worst_year}')
    plt.colorbar(im, ax=ax, label='Relative Anomaly')
    
    # Best year
    ax = axes[0, 1]
    best_data = relative_anomaly.sel({time_dim: best_year}, method='nearest')
    im = ax.pcolormesh(best_data.lon, best_data.lat, best_data,
                       cmap='RdBu', shading='auto', vmin=-0.5, vmax=0.5)
    ax.set_title(f'Best Year: {best_year}')
    plt.colorbar(im, ax=ax, label='Relative Anomaly')
    
    # Anomaly time series for specific regions
    ax = axes[1, 0]
    # Define some regions (adjust as needed)
    regions = {
        'Global': {'lat': slice(-90, 90), 'lon': slice(-180, 180)},
        'North America': {'lat': slice(25, 50), 'lon': slice(-130, -60)},
        'Europe': {'lat': slice(35, 60), 'lon': slice(-10, 40)},
        'East Asia': {'lat': slice(20, 45), 'lon': slice(100, 140)}
    }
    
    for region_name, bounds in regions.items():
        try:
            region_data = relative_anomaly.sel(**bounds).mean(dim=['lat', 'lon'])
            region_data.plot(ax=ax, label=region_name, alpha=0.7)
        except:
            pass  # Skip if region is outside data bounds
    
    ax.set_title('Regional Yield Anomalies')
    ax.set_xlabel('Year')
    ax.set_ylabel('Relative Anomaly')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle=':', alpha=0.5)
    
    # Trend analysis
    ax = axes[1, 1]
    # Calculate linear trend at each grid point
    from scipy import stats
    
    # Get years as numbers
    years = np.arange(len(relative_anomaly[time_dim]))
    trend_map = np.zeros((len(relative_anomaly.lat), len(relative_anomaly.lon)))
    
    for i in range(len(relative_anomaly.lat)):
        for j in range(len(relative_anomaly.lon)):
            ts = relative_anomaly.isel(lat=i, lon=j).values
            if not np.all(np.isnan(ts)):
                valid = ~np.isnan(ts)
                if valid.sum() > 5:  # Need at least 5 points
                    slope, _, _, _, _ = stats.linregress(years[valid], ts[valid])
                    trend_map[i, j] = slope * 10  # Trend per decade
                else:
                    trend_map[i, j] = np.nan
            else:
                trend_map[i, j] = np.nan
    
    im = ax.pcolormesh(relative_anomaly.lon, relative_anomaly.lat, trend_map,
                       cmap='RdBu_r', shading='auto', vmin=-0.1, vmax=0.1)
    ax.set_title('Yield Anomaly Trend (per decade)')
    plt.colorbar(im, ax=ax, label='Trend [fraction/decade]')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'yield_anomaly_extremes.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_hazard_statistics(hazard, output_dir):
    """
    Plot CLIMADA hazard statistics
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Event intensity distribution
    ax = axes[0, 0]
    # Get all non-zero intensities
    intensities = hazard.intensity.data
    ax.hist(intensities, bins=50, density=True, alpha=0.7, edgecolor='black')
    ax.set_xlabel('Anomaly Intensity')
    ax.set_ylabel('Density')
    ax.set_title('Distribution of Hazard Intensities')
    ax.grid(True, alpha=0.3)
    
    # 2. Spatial coverage by event
    ax = axes[0, 1]
    coverage = (hazard.intensity != 0).sum(axis=1).A1 / hazard.intensity.shape[1]
    ax.bar(range(len(coverage)), coverage)
    ax.set_xlabel('Event')
    ax.set_ylabel('Fraction of Area Affected')
    ax.set_title('Spatial Coverage by Event')
    
    # 3. Mean intensity map
    ax = axes[1, 0]
    mean_intensity = np.array(hazard.intensity.mean(axis=0)).flatten()
    hazard.centroids.plot_scatter(values=mean_intensity, ax=ax, cmap='RdBu',
                                  vmin=-0.2, vmax=0.2)
    ax.set_title('Mean Anomaly Intensity')
    
    # 4. Maximum intensity map
    ax = axes[1, 1]
    max_intensity = np.array(np.abs(hazard.intensity).max(axis=0)).flatten()
    hazard.centroids.plot_scatter(values=max_intensity, ax=ax, cmap='Reds',
                                  vmin=0, vmax=0.5)
    ax.set_title('Maximum Absolute Anomaly')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'hazard_statistics.png', dpi=300, bbox_inches='tight')
    plt.close()

# ============================================================================
# 6. HELPER FUNCTIONS
# ============================================================================

def process_local_files(download_dir):
    """
    Process any NetCDF files already in the download directory
    """
    print("\n--- Checking for local NetCDF files ---")
    
    nc_files = list(download_dir.glob('*.nc')) + list(download_dir.glob('*.nc4'))
    
    if nc_files:
        print(f"Found {len(nc_files)} NetCDF files in {download_dir}:")
        for f in nc_files:
            print(f"  - {f.name} ({f.stat().st_size / 1024 / 1024:.2f} MB)")
        return nc_files
    else:
        print(f"No NetCDF files found in {download_dir}")
        return []

def example_impact_calculation(hazard, output_dir):
    """
    Example of how to use the yield anomaly hazard for impact calculation
    """
    print("\n--- Example Impact Calculation ---")
    
    # Create a simple exposure (uniform crop production)
    from climada.entity import Exposures
    
    exp = Exposures()
    exp.gdf = hazard.centroids.to_geodataframe()
    exp.gdf['value'] = 1000  # 1000 USD per grid cell (example)
    exp.value_unit = 'USD'
    exp.meta = {'crop': 'maize', 'description': 'Example uniform exposure'}
    
    # Create impact function for yield anomaly
    impf = ImpactFunc()
    impf.id = 1
    impf.haz_type = 'YieldAnomaly'
    impf.name = 'Linear yield loss'
    
    # Define impact function (linear response to negative anomalies)
    # Positive anomalies (surplus) -> no impact
    # Negative anomalies (deficit) -> proportional loss
    intensity = np.linspace(-1, 1, 201)
    mdd = np.where(intensity < 0, -intensity, 0)  # Only negative anomalies cause damage
    paa = np.ones_like(intensity)  # All areas affected
    
    impf.intensity = intensity
    impf.mdd = mdd
    impf.paa = paa
    
    # Create impact function set
    impf_set = ImpactFuncSet()
    impf_set.append(impf)
    impf_set.check()
    
    # Calculate impact
    imp = Impact()
    imp.calc(exp, impf_set, hazard)
    
    # Plot results
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Impact function
    ax = axes[0]
    actual_impact = impf.intensity * impf.mdd * impf.paa
    ax.plot(impf.intensity, actual_impact, 'b-', linewidth=2)
    ax.set_xlabel('Yield Anomaly')
    ax.set_ylabel('Impact Factor')
    ax.set_title('Impact Function')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax.axvline(x=0, color='k', linestyle='--', alpha=0.5)
    
    # Annual impacts
    ax = axes[1]
    years = [int(name) for name in hazard.event_name]
    ax.bar(years, imp.at_event, alpha=0.7)
    ax.set_xlabel('Year')
    ax.set_ylabel(f'Impact [{imp.unit}]')
    ax.set_title('Annual Impacts from Yield Deficits')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'example_impacts.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Total impact: {imp.at_event.sum():,.0f} {imp.unit}")
    print(f"Average annual impact: {imp.aai_agg:,.0f} {imp.unit}")
    
    return imp

# ============================================================================
# 7. MAIN WORKFLOW
# ============================================================================

def main():
    """
    Main workflow for downloading and processing ISIMIP3b maize yield data
    """
    print("=== ISIMIP3b Maize Yield Anomaly Analysis ===")
    
    # Step 1: Search for data
    print("\n--- Step 1: Searching for ISIMIP3b maize yield data ---")
    
    # First try searching for yield change data (which is what we found)
    datasets = search_isimip3b_yield_data(crop=CROP, search_absolute_yield=True)
    
    print(f"\nFound {datasets['count']} datasets for {CROP}")
    
    # Check why datasets don't have files
    if datasets['count'] > 0:
        print("\nChecking dataset status...")
        client = ISIMIPClient()
        for i, ds in enumerate(datasets['results'][:3]):  # Check first 3
            print(f"\nDataset {i+1}: {ds.get('name', 'Unknown')}")
            print(f"  Path: {ds.get('path', 'Unknown')}")
            print(f"  Public: {ds.get('public', 'Unknown')}")
            print(f"  Restricted: {ds.get('restricted', 'Unknown')}")
            
            # Check for caveats or notes
            if 'caveats' in ds:
                print(f"  Caveats: {ds['caveats']}")
            if 'resources' in ds:
                print(f"  Resources: {len(ds.get('resources', []))}")
    
    # Step 2: Try to download data
    print("\n--- Step 2: Attempting to download yield data ---")
    
    downloaded_files = []
    
    # First, try using known file IDs
    print("\nTrying to download using known file IDs...")
    file_ids = get_isimip3b_file_ids()
    
    for file_id in file_ids:
        downloaded_file = download_file_by_id(file_id, DOWNLOAD_DIR)
        if downloaded_file:
            downloaded_files.append(downloaded_file)
    
    # If no success with file IDs, try the regular download method
    if not downloaded_files and datasets['count'] > 0:
        print("\nTrying regular download method...")
        downloaded_files = download_yield_files(datasets, DOWNLOAD_DIR, include_all_scenarios=False)
    
    # Step 3: Check for local files
    if not downloaded_files:
        print("\n--- Step 3: Checking for local files ---")
        local_files = process_local_files(DOWNLOAD_DIR)
        
        if local_files:
            print("\nWill process local files instead of downloading.")
            downloaded_files = local_files
        else:
            print("\nNo files available for processing.")
            print("\nPossible solutions:")
            print("1. The working file URL suggests files are available at:")
            print("   https://data.isimip.org/files/FILE_ID/")
            print("2. You can find file IDs by browsing: https://data.isimip.org/")
            print("3. Add more working file IDs to the get_isimip3b_file_ids() function")
            print("4. Download files manually using your browser and place them in:")
            print(f"   {DOWNLOAD_DIR}")
            
            # Try one more thing - download the specific working file
            print("\nAttempting to download the known working file...")
            test_file = download_file_by_id('9afab06d-99c6-4d22-993e-0d67233f965b', DOWNLOAD_DIR)
            if test_file:
                downloaded_files = [test_file]
            else:
                return
    
    print(f"\nTotal files to process: {len(downloaded_files)}")
    
    # Step 4: Process each file
    print("\n--- Step 4: Processing yield data ---")
    all_hazards = []
    
    for nc_file in downloaded_files:
        try:
            # Process yield data
            yield_data, dataset = process_yield_data(nc_file, bbox=BBOX)
            
            # Check what kind of data we have
            print(f"\nData shape: {yield_data.shape}")
            print(f"Data range: [{float(yield_data.min().compute()):.3f}, {float(yield_data.max().compute()):.3f}]")
            
            # Print sample of data to understand structure
            if len(yield_data.dims) >= 2:
                print("\nSample data (first 5x5 grid points, first time):")
                sample = yield_data.isel({d: slice(5) for d in yield_data.dims})
                print(sample.values)
            
            # Determine if this is yield change data
            is_yield_change = 'yieldchange' in nc_file.name.lower()
            
            if is_yield_change:
                print("\nThis is yield change data - already represents anomalies")
                # For yield change data, we can directly use it as anomaly
                # Get time dimension name
                time_dim = 'time' if 'time' in yield_data.dims else 'year'
                
                anomaly_data = {
                    'relative': yield_data,  # Already relative change
                    'zscore': yield_data / yield_data.std(dim=time_dim),  # Approximate z-score
                    'ref_mean': yield_data.mean(dim=time_dim),
                    'ref_std': yield_data.std(dim=time_dim),
                    'absolute': yield_data  # We don't have absolute values
                }
            else:
                # Compute anomalies for absolute yield data
                anomaly_data = compute_yield_anomaly(yield_data, REFERENCE_PERIOD)
            
            # Create output subdirectory for this dataset
            dataset_name = nc_file.stem
            dataset_output_dir = OUTPUT_DIR / dataset_name
            dataset_output_dir.mkdir(exist_ok=True)
            
            # Create visualizations
            print("\nCreating visualizations...")
            try:
                plot_yield_analysis(anomaly_data, dataset_output_dir)
            except Exception as e:
                print(f"Warning: Could not create all plots: {e}")
            
            # Create CLIMADA hazards
            print("\nCreating CLIMADA hazards...")
            
            # Create relative anomaly hazard
            haz_relative = create_anomaly_hazard(anomaly_data, hazard_type='relative')
            haz_relative.tag.description = f"Maize yield {'change' if is_yield_change else 'anomaly'} from {dataset_name}"
            haz_relative.write_hdf5(dataset_output_dir / 'hazard_relative_anomaly.hdf5')
            
            # Plot hazard statistics
            try:
                plot_hazard_statistics(haz_relative, dataset_output_dir)
            except Exception as e:
                print(f"Warning: Could not create hazard plots: {e}")
            
            # Save processed data
            print("\nSaving processed data...")
            
            # Save anomaly data as NetCDF
            if is_yield_change:
                anomaly_ds = xr.Dataset({
                    'yield_change': yield_data,
                    'yield_change_zscore': anomaly_data['zscore']
                })
                anomaly_ds.attrs['description'] = f'Processed maize yield change from {dataset_name}'
            else:
                anomaly_ds = xr.Dataset({
                    'yield_absolute': yield_data,
                    'yield_anomaly_relative': anomaly_data['relative'],
                    'yield_anomaly_zscore': anomaly_data['zscore'],
                    'yield_reference_mean': anomaly_data['ref_mean'],
                    'yield_reference_std': anomaly_data['ref_std']
                })
                anomaly_ds.attrs['description'] = f'Processed maize yield anomalies from {dataset_name}'
                anomaly_ds.attrs['reference_period'] = f'{REFERENCE_PERIOD[0]}-{REFERENCE_PERIOD[1]}'
            
            anomaly_ds.to_netcdf(dataset_output_dir / 'processed_data.nc')
            
            all_hazards.append({
                'name': dataset_name,
                'hazard_relative': haz_relative,
                'anomaly_data': anomaly_data,
                'is_yield_change': is_yield_change
            })
            
            print(f"\nCompleted processing: {dataset_name}")
            
            # Run example impact calculation
            try:
                example_impact_calculation(haz_relative, dataset_output_dir)
            except Exception as e:
                print(f"Warning: Could not run impact calculation: {e}")
            
        except Exception as e:
            print(f"\nError processing {nc_file.name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Step 5: Summary
    print("\n--- Step 5: Analysis Summary ---")
    print(f"Successfully processed {len(all_hazards)} datasets")
    print(f"Results saved to: {OUTPUT_DIR}")
    
    if all_hazards:
        # Create summary report
        summary_file = OUTPUT_DIR / 'analysis_summary.txt'
        with open(summary_file, 'w') as f:
            f.write("ISIMIP3b Maize Yield Anomaly Analysis Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Analysis Date: {pd.Timestamp.now()}\n")
            f.write(f"Crop: Maize\n")
            f.write(f"Reference Period: {REFERENCE_PERIOD[0]}-{REFERENCE_PERIOD[1]}\n")
            f.write(f"Bounding Box: {BBOX if BBOX else 'Global'}\n\n")
            
            f.write("Processed Datasets:\n")
            for item in all_hazards:
                f.write(f"\n- {item['name']}\n")
                f.write(f"  Type: {'Yield Change' if item['is_yield_change'] else 'Absolute Yield'}\n")
                haz = item['hazard_relative']
                f.write(f"  Events: {len(haz.event_id)}\n")
                f.write(f"  Centroids: {haz.centroids.size}\n")
                f.write(f"  Mean intensity: {haz.intensity.mean():.4f}\n")
                f.write(f"  Max intensity: {haz.intensity.max():.4f}\n")
                f.write(f"  Min intensity: {haz.intensity.min():.4f}\n")
        
        print(f"\nAnalysis complete! Summary saved to: {summary_file}")
    else:
        print("\nNo datasets were successfully processed.")
    
    return all_hazards

# ============================================================================
# RUN THE ANALYSIS
# ============================================================================

#if __name__ == "__main__":
hazards = main()