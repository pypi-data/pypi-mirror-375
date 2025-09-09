# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sorcerer Forecasts is a Python library for fetching and processing weather forecast data from cloud sources. It provides a caching mechanism and supports multiple forecast regions with 4D spatio-temporal querying (latitude, longitude, altitude, time).

## Development Setup

### Package Management
This project uses `uv` as the package manager. Key commands:
```bash
# Install dependencies
uv pip install -e .

# Activate virtual environment
source .venv/bin/activate
```

### Dependencies
Core dependencies managed in `pyproject.toml`:
- `xarray` - Multi-dimensional data handling
- `s3fs` - AWS S3 filesystem access
- `h5netcdf` - NetCDF file format support
- `pyjwt` - JWT token handling for API authentication

## Architecture

### Core Components

1. **ForecastService** (`services/forecast_service.py`): Main service class that handles forecast retrieval with caching
   - Generic service that works with any `ForecastSource` implementation
   - Manages local NetCDF cache of downloaded forecasts
   - Returns forecast data at specific 4D points

2. **ForecastSource** (`sources/base.py`): Abstract base class for forecast data sources
   - Defines interface for fetching xarray datasets
   - Provides forecast ID generation for caching

3. **Stratocast** (`sources/stratocast.py`): Implementation for Stratocast weather data
   - Fetches stratospheric wind forecast data from S3
   - Handles JWT-based authentication
   - Supports multiple forecast regions with 15-minute temporal resolution
   - Returns data with variables: `pres`, `u`, `v`, `h` (pressure, wind components, height)

4. **Forecast** (`entity/forecast.py`): Manages loaded forecast datasets
   - Handles 4D interpolation to extract data at specific points
   - Manages temporal flooring and spatial indexing
   - Supports level-based vertical interpolation using height field

5. **Geographic Types** (`entity/geo.py`):
   - `Point2`: latitude/longitude
   - `Point3`: adds altitude
   - `Point4`: adds time dimension
   - `Region`: bounding box with containment checking

6. **Region Management** (`utils/region.py`): Predefined forecast regions
   - CONUS, EU-Central, AF-East, Region4, Global
   - Automatic region selection based on location

## Key Implementation Details

- Forecast data is stored as NetCDF files with dimensions: time, level, latitude, longitude
- Temporal resolution is automatically detected from the dataset
- Caching uses forecast IDs based on time, resolution, and region
- S3 access uses AWS credentials embedded in JWT tokens
- Demo users have special directory routing in S3