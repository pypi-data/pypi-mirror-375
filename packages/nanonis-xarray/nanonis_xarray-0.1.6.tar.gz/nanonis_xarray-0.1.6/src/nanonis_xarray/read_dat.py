"""Read a Nanonis spectroscopy .dat file into a xarray Dataset."""

from pathlib import Path

import pandas as pd
import xarray as xr

from .data import parse_data
from .header import parse_header_lines

_encoding = "utf-8"
_data_tag = "[DATA]\n"


def read_dat(
    path: Path | str, *, quantify_vars: bool = True, squeeze: bool = True
) -> xr.Dataset:
    """Read a Nanonis spectroscopy .dat file into a xarray Dataset."""
    path = Path(path)
    with path.open(encoding=_encoding) as file:
        header_lines = []
        for line in file:
            if line == "\n":
                continue
            if line == _data_tag:
                break
            header_lines.append(line)
        else:
            msg = f"Invalid Nanonis .dat file. Tag {_data_tag} not found in {path}"
            raise RuntimeError(msg)
        raw_data = pd.read_csv(file, sep="\t")
    header = parse_header_lines(header_lines)
    dataset = parse_data(raw_data)
    dataset.attrs |= header
    if quantify_vars:
        # Enable pint phyisical units.
        dataset = dataset.pint.quantify()
    if squeeze:
        dataset = dataset.squeeze()
    return dataset
