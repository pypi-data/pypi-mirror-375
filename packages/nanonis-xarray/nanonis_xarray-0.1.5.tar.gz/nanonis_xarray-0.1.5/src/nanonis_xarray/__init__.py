"""Read a Nanonis spectroscopy .dat file into an xarray Dataset."""

from importlib.metadata import version

# Use pint_xarray's unit registry.
from pint_xarray import unit_registry

from .read_dat import read_dat

__version__ = version("nanonis-xarray")
__all__ = ["read_dat", "unit_registry"]
