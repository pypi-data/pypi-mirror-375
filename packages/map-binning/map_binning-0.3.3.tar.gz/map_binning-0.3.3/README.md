# Map Binning Tool

[![Conda version](https://img.shields.io/conda/vn/conda-forge/map-binning.svg)](https://anaconda.org/conda-forge/map-binning)
[![PyPI version](https://img.shields.io/pypi/v/map-binning.svg)](https://pypi.org/project/map-binning/)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD Pipeline](https://github.com/chiaweh2/map_binning/actions/workflows/ci.yml/badge.svg)](https://github.com/chiaweh2/map_binning/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/chiaweh2/map_binning/branch/main/graph/badge.svg)](https://codecov.io/gh/chiaweh2/map_binning)

A Python package for spatial resampling and binning of geospatial data, specifically designed for oceanographic datasets. This tool enables efficient downsampling of high-resolution gridded data onto coarser grids while preserving spatial accuracy through intelligent neighborhood averaging.

## Citation
[![DOI](https://zenodo.org/badge/1050687709.svg)](https://doi.org/10.5281/zenodo.17095448)

If you use this tool in your research, please cite:

```bibtex
@software{map_binning_2025,
  author = {Chia-Wei Hsu},
  title = {Map Binning Tool: Spatial Resampling for Oceanographic Data},
  url = {https://github.com/chiaweh2/map_binning},
  doi = {10.5281/zenodo.17095448},
  year = {2025}
}
```

## Overview

The Map Binning Tool provides a robust solution for spatial data aggregation, particularly useful for:
- Downsampling high-resolution oceanographic data (e.g., sea level anomaly, ocean currents)
- Creating consistent multi-resolution datasets
- Reducing computational load while maintaining spatial representativeness
- Processing time-series of gridded data efficiently

The package uses k-d tree algorithms for fast spatial queries and supports both in-memory processing and persistent caching of spatial indices for repeated operations.

## Key Features

- **Efficient Spatial Binning**: Uses scipy's cKDTree for fast nearest-neighbor searches
- **Flexible Grid Support**: Works with any xarray-compatible gridded dataset
- **Automatic Radius Calculation**: Intelligently determines search radius based on target grid spacing
- **Persistent Caching**: Save and reuse spatial indices using pickle serialization
- **Time Series Support**: Handles datasets with temporal dimensions
- **Memory Efficient**: Processes large datasets without excessive memory usage
- **Oceanographic Focus**: Optimized for CMEMS and similar oceanographic data formats

## Installation

### From conda-forge (Recommended)

```bash
conda install -c conda-forge map-binning
```

### From PyPI

```bash
pip install map-binning
```

### With optional dependencies for development

```bash
pip install map-binning[dev]
```


## Developer Installation

### From source
```bash
git clone <repository-url>
cd map_binning
pip install -e .
```

## Quick Start

### Basic Usage

```python
import xarray as xr
from map_binning import Binning

# Load your datasets
ds_high = xr.open_dataset('high_resolution_data.nc')
ds_low = xr.open_dataset('low_resolution_grid.nc')

# Initialize the binning tool
binning = Binning(
    ds_high=ds_high,
    ds_low=ds_low,
    var_name='sla',  # variable in the dataset to bin (e.g., sea level anomaly)
    xdim_name='longitude',  # longitude dimension name
    ydim_name='latitude',   # latitude dimension name
    search_radius=0.1  # optional: search radius in degrees
)

# Perform binning
result = binning.mean_binning()
```

### Advanced Usage with Caching

```python
# Create binning index and save it for reuse
result = binning.mean_binning(
    precomputed_binning_index=False,
    pickle_filename="my_binning_index.pkl",
    pickle_location="./cache"
)

# Reuse the saved index for subsequent operations
result = binning.mean_binning(
    precomputed_binning_index=True,
    pickle_filename="my_binning_index.pkl",
    pickle_location="./cache"
)
```

### Time Series Processing

The tool automatically handles time dimensions:

```python
# Works seamlessly with time-varying datasets
# Input: (time, lat, lon) -> Output: (time, lat_low, lon_low)
result = binning.mean_binning()
```
## Configuration for CMEMS data download

### Environment Variables

Copy `.env.template` to `.env` and configure:

```bash
# Copernicus Marine Service credentials (if using CMEMS data)
COPERNICUSMARINE_SERVICE_USERNAME=<your_username>
COPERNICUSMARINE_SERVICE_PASSWORD=<your_password>
```

## API Reference

### Binning Class

#### Constructor Parameters
- `ds_high` (xr.Dataset): High-resolution source dataset
- `ds_low` (xr.Dataset): Low-resolution target grid dataset  
- `var_name` (str): Name of the variable to bin
- `xdim_name` (str, optional): Longitude dimension name (default: 'lon')
- `ydim_name` (str, optional): Latitude dimension name (default: 'lat')
- `search_radius` (float, optional): Search radius in degrees (auto-calculated if None)

#### Methods

**`create_binning_index()`**
Creates a spatial mapping between high and low resolution grids.

**`mean_binning(precomputed_binning_index=False, pickle_filename=None, pickle_location=None)`**
Performs spatial binning using mean aggregation.

Parameters:
- `precomputed_binning_index` (bool): Use pre-saved spatial index
- `pickle_filename` (str): Filename for saving/loading spatial index
- `pickle_location` (str): Directory path for pickle files

Returns: `xr.DataArray` with binned data on the target grid

## Project Structure

```
map_binning/
├── map_binning/           # Main package directory
│   ├── __init__.py        # Package initialization
│   ├── binning.py         # Core binning algorithms
│   ├── index_store.py     # Pickle serialization utilities
│   └── main.py            # Command-line interface
├── notebooks/             # Jupyter notebooks for examples
│   └── cmems_nrt_coastal_bin.ipynb
├── tests/                 # Unit tests
│   ├── __init__.py
│   └── ...
├── pyproject.toml         # Project configuration
├── environment.yml        # Conda environment specification
├── .env.template          # Environment variables template
└── README.md              # This file
```



## Performance Considerations

- **Memory Usage**: The tool processes data in chunks and uses efficient numpy operations
- **Spatial Index Caching**: Save computed spatial indices to avoid recalculation
- **Grid Resolution**: Performance scales with the product of grid sizes
- **Search Radius**: Smaller radii improve performance but may miss relevant data points

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the test suite (`pytest`)
5. Format your code (`black map_binning/`)
6. Submit a pull request

### Development Setup

```bash
# Clone and setup development environment
git clone <repository-url>
cd map-binning-project
conda env create -f environment.yml
conda activate map-binning
pip install -e .[dev]

# Run tests
pytest

# Format code
black map_binning/

# Type checking
mypy map_binning/
```


## License

This project is licensed under the MIT License - see the LICENSE file for details.


## Support

- **Issues**: Please report bugs and feature requests via GitHub Issues
- **Documentation**: Additional examples available in the `notebooks/` directory
- **Contact**: Chia-Wei Hsu (chiaweh2@uci.edu)

## Acknowledgments

- Built with support for Copernicus Marine Environment Monitoring Service (CMEMS) data
- Utilizes scipy's efficient spatial algorithms
- Designed for the oceanographic research community