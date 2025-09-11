# Xarray plugin to read Nanonis spectroscopy .dat files

[![pypi](https://img.shields.io/pypi/v/nanonis-xarray)](https://pypi.org/project/nanonis-xarray/)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/nanonis-xarray)](https://anaconda.org/conda-forge/nanonis-xarray)
[![pypi downloads](https://img.shields.io/pypi/dm/nanonis-xarray)](https://pypistats.org/packages/nanonis-xarray)
[![license](https://img.shields.io/github/license/angelo-peronio/nanonis-xarray)](https://github.com/angelo-peronio/nanonis-xarray/blob/master/LICENSE)
[![python](https://img.shields.io/pypi/pyversions/nanonis-xarray)](https://pypi.org/project/nanonis-xarray/)
[![SPEC 0 — Minimum Supported Dependencies](https://img.shields.io/badge/SPEC-0-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0000/)
[![ci](https://github.com/angelo-peronio/nanonis-xarray/actions/workflows/ci.yaml/badge.svg)](https://github.com/angelo-peronio/nanonis-xarray/actions/workflows/ci.yaml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/angelo-peronio/nanonis-xarray/master.svg)](https://results.pre-commit.ci/latest/github/angelo-peronio/nanonis-xarray/master)
[![codecov](https://codecov.io/github/angelo-peronio/nanonis-xarray/graph/badge.svg)](https://codecov.io/github/angelo-peronio/nanonis-xarray)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/format.json)](https://github.com/astral-sh/ruff)
[![DOI](https://zenodo.org/badge/1032126987.svg)](https://doi.org/10.5281/zenodo.17095214)

[`nanonis-xarray`](https://github.com/angelo-peronio/nanonis-xarray) is a [`xarray`](https://xarray.dev/) plugin to read spectroscopy measurements saved in text
format (`.dat`) by a [Nanonis Mimea](https://www.specs-group.com/nanonis/products/mimea/)
SPM control system from [SPECS Surface Nano Analysis GmbH](https://www.specs-group.com/).

The data is read into a [`xarray.Dataset`](https://docs.xarray.dev/en/stable/getting-started-guide/why-xarray.html#core-data-structures), where each measured channel (tunnelling current, AFM oscillation amplitude, …) is a [`xarray.DataArray`](https://docs.xarray.dev/en/stable/user-guide/data-structures.html#dataarray) with up to three dimensions:

* The independent variable of the measurement, such as bias voltage or tip z position;
* The sweep number, if the measurement has been repeated multiple times;
* The sweep direction (forward or backward), if the independent variable has been swept in both directions.

```python
>>> import xarray as xr

>>> data = xr.open_dataset("tests/data/z.dat")
>>> data.coords
Coordinates:
  * z_rel      (z_rel) float64 2kB [m] -2.1e-10 -2.065e-10 ... 4.865e-10 4.9e-10
  * sweep      (sweep) int64 24B 1 2 3
  * direction  (direction) object 16B 'bw' 'fw'

```

[pint-xarray](https://xarray.dev/blog/introducing-pint-xarray) is used to associate a physical unit to each channel, unless `xr.open_dataset()` is called with `quantify_vars=False`:

```python
>>> data["current"].pint.units
<Unit('ampere')>

```

The header of the measurement is stored in the `attrs` nested dictionary:

```python
>>> data.attrs["Z Spectroscopy"]["Number of sweeps"]
3
>>> data.attrs["Z Spectroscopy"]["backward sweep"]
True

```

Physical quantities are stored as [`pint.Quantity`](https://pint.readthedocs.io/en/stable/getting/tutorial.html#defining-a-quantity), timestamps as [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime-objects), and paths as [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#basic-use):

```python
>>> data.attrs["NanonisMain"]["RT Frequency"]
<Quantity(10000.0, 'hertz')>
>>> data.attrs["Date"]
datetime.datetime(2015, 3, 27, 11, 49, 5)

```

## 🚧 Work in progress 🚧

This library is under development: expect breaking changes. Nanonis binary formats (`.sxm`, `.3ds`) are currently not supported, and can be read by similar projects:

* [`nanonispy2`](https://github.com/ceds92/nanonispy2)
* [`xarray-nanonis`](https://github.com/John3859/xarray-nanonis)
* ... and [many more](https://pypi.org/search/?q=nanonis).

## How to cite

Cite `nanonis-xarray` in your published work using the metadata
in [`CITATION.cff`](CITATION.cff), or this general BibTeX entry:

```bibtex
@misc{Peronio_nanonis-xarray_2025,
title = {nanonis-xarray},
author = {Peronio, Angelo},
url = {https://github.com/angelo-peronio/nanonis-xarray},
doi = {10.5281/zenodo.17095214},
year = {2025},
month = {5}
}

```

Specific DOIs for each released version are listed on [Zenodo](https://doi.org/10.5281/zenodo.17095214),
but are not included in `CITATION.cff` due to a [limitation](https://github.com/zenodo/zenodo-rdm/issues/831)
of Zenodo itself.
