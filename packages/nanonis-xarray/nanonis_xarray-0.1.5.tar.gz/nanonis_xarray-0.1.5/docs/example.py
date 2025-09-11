"""Usage of nanonis_xarray."""

# ruff: noqa: INP001, B018, T201
# %%
# ! %reload_ext autoreload
# ! %autoreload complete
# ! %matplotlib widget
from pathlib import Path

import seaborn as sns
import xarray as xr
from matplotlib import pyplot as plt

sns.set_theme()

project_root = Path(__file__).parents[1]
data_path = project_root / "tests" / "data" / "z.dat"
data = xr.open_dataset(data_path)
data
# %%
print(data.coords["z_rel"].attrs)
# %%
fig, ax = plt.subplots()
data["current"].sel(sweep=2, direction="fw").plot()
# %%
fig, ax = plt.subplots()
data["current"].mean(dim=["sweep"]).sel(direction="fw").pint.dequantify(
    format="~P"
).plot()
# %%
fig, ax = plt.subplots()
data["current"].std(dim=["sweep"]).sel(direction="fw").pint.dequantify(
    format="~P"
).plot()
# %%
