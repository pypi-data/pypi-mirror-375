"""Test open_dataset."""

from datetime import datetime
from pathlib import Path

import xarray as xr

from nanonis_xarray import unit_registry as u

from .conftest import data_folder


def test_a() -> None:
    """Test opening a .dat file."""
    data_path = data_folder / "a.dat"
    data = xr.open_dataset(data_path)

    assert "sweep" not in data.data_vars
    assert "direction" not in data.data_vars
    assert data.attrs["Bias Spectroscopy"]["MultiLine Settings"][
        "Integration"
    ] == 0.1 * u("ms")
    assert isinstance(data.attrs["NanonisMain"]["Session Path"], Path)
    assert isinstance(data.attrs["Date"], datetime)


def test_df_v() -> None:
    """Test opening a .dat file."""
    data_path = data_folder / "df_v.dat"
    data = xr.open_dataset(data_path)

    assert "sweep" not in data.data_vars
    assert data.direction.size == 2
    assert isinstance(data.attrs["NanonisMain"]["Session Path"], Path)
    assert isinstance(data.attrs["Date"], datetime)


def test_z() -> None:
    """Test opening a .dat file."""
    data_path = data_folder / "z.dat"
    data = xr.open_dataset(data_path)

    assert data.attrs["Bias Spectroscopy"]["backward sweep"] is True
    assert data.sweep.size == 3
    assert data.direction.size == 2
    assert isinstance(data.attrs["NanonisMain"]["Session Path"], Path)
    assert isinstance(data.attrs["Date"], datetime)


def test_drop_variables() -> None:
    """Test drop_variables parameter."""
    data_path = data_folder / "a.dat"
    data_1 = xr.open_dataset(data_path)
    assert "phase" in data_1

    data_2 = xr.open_dataset(data_path, drop_variables="phase")
    assert "phase" not in data_2


def test_squeeze() -> None:
    """Test squeeze parameter."""
    data_path = data_folder / "a.dat"
    data_1 = xr.open_dataset(data_path)
    assert len(data_1.dims) == 1

    data_2 = xr.open_dataset(data_path, squeeze=False)
    assert len(data_2.dims) == 3


def test_quantify_vars() -> None:
    """Test quantify_vars parameter."""
    data_path = data_folder / "a.dat"
    data_1 = xr.open_dataset(data_path)
    assert data_1["current"].pint.units == u("ampere")

    data_2 = xr.open_dataset(data_path, quantify_vars=False)
    assert data_2["current"].pint.units is None
