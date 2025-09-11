"""Test physical units."""

import xarray as xr

from nanonis_xarray import unit_registry as u

from .conftest import data_folder


def test_units() -> None:
    """Test physical units."""
    data_path = data_folder / "a.dat"
    data = xr.open_dataset(data_path)
    wannabe_power = data["current"] * data.attrs["Bias"]["Bias"]
    assert wannabe_power.pint.units == u("watt")
