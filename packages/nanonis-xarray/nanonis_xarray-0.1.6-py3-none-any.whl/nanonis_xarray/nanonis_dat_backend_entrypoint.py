"""Xarray backend plugin.

See https://docs.xarray.dev/en/stable/internals/how-to-add-new-backend.html#rst-backend-entrypoint
"""

from pathlib import Path

from xarray.backends import BackendEntrypoint

from .read_dat import read_dat


class NanonisDatBackendEntrypoint(BackendEntrypoint):
    """Xarray backend plugin."""

    def open_dataset(self, filename_or_obj, *, drop_variables=None, **kwargs):
        """Read a Nanonis .dat file."""
        dataset = read_dat(Path(filename_or_obj), **kwargs)
        if drop_variables:
            dataset = dataset.drop_vars(drop_variables)
        return dataset

    def guess_can_open(self, filename_or_obj):
        """Guess wether we are dealing with a Nanonis .dat file."""
        path = Path(filename_or_obj)
        return path.suffix == ".dat"

    open_dataset_parameters = (
        "filename_or_obj",
        "drop_variables",
        "quantify_vars",
        "squeeze",
    )

    description = "Read Nanonis spectroscopy .dat files into xarray Datasets."

    url = "https://github.com/angelo-peronio/nanonis-xarray"
