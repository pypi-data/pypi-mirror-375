"""Auto-nesting dict, accessible also with a sequence of keys."""

import operator
from collections import abc, defaultdict
from functools import reduce
from typing import Any


def autonesting_defaultdict_factory() -> defaultdict:
    """Return a defaultdict, whose default_factory returns a defaultdict, ...

    ... whose default_factory returns a defaultdict,
    whose default_factory returns a defaultdict,
    whose default_factory returns a defaultdict, ...
    """
    # https://stackoverflow.com/a/8702435
    return defaultdict(autonesting_defaultdict_factory)


def nested_defaultdict_to_dict(obj: Any) -> dict:
    """Convert a nested defaultdict to a dict."""
    # https://stackoverflow.com/a/26496899/11503785
    if isinstance(obj, defaultdict):
        return {key: nested_defaultdict_to_dict(value) for key, value in obj.items()}
    return obj


class AutonestingDict(abc.MutableMapping):
    """Auto-nesting dict, accessible also with a sequence of keys."""

    def __init__(self) -> None:
        self.autonesting_defaultdict = autonesting_defaultdict_factory()

    def __getitem__(self, key):
        """Return self[key]."""
        return self.autonesting_defaultdict.__getitem__(key)

    def __setitem__(self, key, item):
        """Set self[key] to value."""
        return self.autonesting_defaultdict.__setitem__(key, item)

    def __delitem__(self, key):
        """Delete self[key]."""
        return self.autonesting_defaultdict.__delitem__(key)

    def __iter__(self):
        """Implement iter(self)."""
        return self.autonesting_defaultdict.__iter__()

    def __len__(self):
        """Return len(self)."""
        return self.autonesting_defaultdict.__len__()

    def get_by_seq(self, keys: abc.Sequence):
        """Get by sequence of keys."""
        # https://stackoverflow.com/a/14692747
        return reduce(operator.getitem, keys, self.autonesting_defaultdict)

    def set_by_seq(self, keys: abc.Sequence, value):
        """Set by sequence of keys."""
        self.get_by_seq(keys[:-1])[keys[-1]] = value

    def del_by_seq(self, keys: abc.Sequence):
        """Delete by sequence of keys."""
        del self.get_by_seq(keys[:-1])[keys[-1]]

    def asdict(self) -> dict:
        """Convert to dict."""
        return nested_defaultdict_to_dict(self.autonesting_defaultdict)
