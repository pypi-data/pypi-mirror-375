# File: src/samudra_ai/preprocess_dcpp.py
import xarray as xr
import pandas as pd
import numpy as np
from .utils import standardize_dims

def preprocess_dcpp(
    file_path: str,
    var_name: str,
    lat_range: tuple = None,
    lon_range: tuple = None,
    time_range: tuple = None
    ) -> xr.DataArray:
    """
    Preprocessing data DCPP agar konsisten dengan CMIP6:
    - Hapus dimensi tambahan (initial_time, ensemble, member, zlev, dll).
    - Opsional: slicing lat/lon/time agar tidak full global.
    - Standarisasi ke format (time, lat, lon).
    """

    ds = xr.open_dataset(file_path, engine="h5netcdf", decode_times=True)

    if var_name not in ds:
        raise ValueError(f"Variabel {var_name} tidak ada dalam file {file_path}")

    da = ds[var_name]

    # Hapus dimensi yang tidak relevan
    for dim in ["initial_time", "ensemble", "member", "zlev"]:
        if dim in da.dims:
            da = da.isel({dim: 0}).squeeze(dim)

    # Buang dimensi extra kalau masih ada
    while len(da.dims) > 3:
        for d in list(da.dims):
            if d not in ["time", "lat", "lon"]:
                da = da.isel({d: 0}).squeeze(d)

    # Standarisasi nama dimensi
    da = standardize_dims(da)

    # --- Opsional: slicing waktu ---
    if time_range:
        start_dt = pd.to_datetime(time_range[0])
        end_dt = pd.to_datetime(time_range[1])
        da = da.sel(time=slice(start_dt, end_dt))

    # --- Opsional: slicing spasial ---
    if lat_range:
        da = da.sel(lat=slice(*lat_range))
    if lon_range:
        da = da.sel(lon=slice(*lon_range))

    return da
