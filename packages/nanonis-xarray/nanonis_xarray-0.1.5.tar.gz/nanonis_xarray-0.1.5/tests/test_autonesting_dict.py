"""Test AutoNestingDict."""

import pytest

from nanonis_xarray.autonesting_dict import AutonestingDict


def test_autonesting_dict() -> None:
    """Test AutoNestingDict."""
    adict = AutonestingDict()

    adict.set_by_seq([1, 2, 3], "a value")
    adict[11] = "another value"
    assert adict[1][2][3] == "a value"
    assert adict.get_by_seq([1, 2, 3]) == "a value"
    assert adict.get_by_seq([1, 2]) == {3: "a value"}

    dict_1 = adict.asdict()
    assert dict_1[1][2][3] == "a value"

    with pytest.raises(TypeError):
        _ = adict.get_by_seq(1)

    assert len(adict) == 2
    adict.del_by_seq([1, 2])
    assert adict == {1: {}, 11: "another value"}
    assert len(list(iter(adict))) == 2

    del adict[11]
    assert len(adict) == 1
