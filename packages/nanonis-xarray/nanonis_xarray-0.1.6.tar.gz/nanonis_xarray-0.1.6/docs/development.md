# Development notes for `nanonis-xarray`

## ToDo

* Decide dimension name: `sweep`, or `repetition`, or `rep`.
* Units as text
* Use `example.py` to evaluate the user experience.
    * Plot.
    * Calculate averages.
    * Rotate lock-in x and y.

## Ideas

* Do we want to normalize the header keys?
* Do we want to have the header to be accessible like `data.attrs.key.subkey`?

## Prio 2

* Enum instead of fw/bw (?)
* CategoricalIndex for direction (?)
* Which text encoding does Nanonis actually use?

## Notes

* It seems Nanonis ships Python routines <https://www.specs-group.com/nanonis/products/mimea/mimea-software/#c1315>
* Nanonis has two packages on PyPI:
    * [`nanonis-tramea`](https://pypi.org/project/nanonis-tramea/)
    * [`nanaonis-spm`](https://pypi.org/project/nanonis-spm/)
