"""Parse the header."""

import re
from datetime import datetime
from pathlib import Path

from . import unit_registry
from .autonesting_dict import AutonestingDict

# Nanonis quirk: these appear between round brackets like physical units, but are not.
units_to_ignore = [
    "on/off",  # Piezo Calibration>Drift correction status
    "xn",  # Bias Spectroscopy>MultiLine Settings
]


def parse_header_lines(lines):
    """Parse header lines."""
    keys_values = [split_header_line(line) for line in lines]
    keys_values = [
        item
        for keys, value in keys_values
        for item in parse_multiline_settings(keys, value)
    ]
    keys_values = [parse_value(keys, value) for keys, value in keys_values]
    header = AutonestingDict()
    for keys, value in keys_values:
        header.set_by_seq(keys, value)
    return header.asdict()


def split_header_line(line):
    """Split a header line into a list of keys and a value."""
    # Strip \t\n from the end of each header line.
    key, value = line[:-2].split("\t")
    keys = key.split(">")
    return keys, value


def parse_multiline_settings(keys, value):
    """Handle the quirky "Multiline Settings" key."""
    if keys[-1].startswith("MultiLine Settings"):
        key, subkeys = (chunk.strip() for chunk in keys[-1].split(":"))
        subkeys = [chunk.strip() for chunk in subkeys.split(",")]
        values = value.split(",")
        for subkey, value_ in zip(subkeys, values, strict=True):
            yield [*keys[:-1], key, subkey], value_
    else:
        yield keys, value


def parse_value(keys, value):
    """Parse values."""
    value = parse_bool_int_float(value)
    keys[-1], unit_str = split_unit(keys[-1])
    if unit_str not in [None, *units_to_ignore]:
        value *= unit_registry(unit_str)
    # Special cases.
    match keys:
        case ["Date"]:
            value = datetime.strptime(value, r"%d.%m.%Y %H:%M:%S")  # noqa: DTZ007
        case [_, "Channels" | "channels"]:
            value = value.split(";")
        case ["Scan", "Scanfield"]:
            value = [float(chunk) for chunk in value.split(";")]
        case ["NanonisMain", "Session Path"]:
            value = Path(value)
    return keys, value


def parse_bool_int_float(value: str) -> bool | int | float | str:
    """Attempt to parse a string into a bool, or an int, or a float."""
    if value == "TRUE":
        return True
    if value == "FALSE":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


units_regexp = re.compile(r"(?P<key>.*) \((?P<units>.*)\)$")


def split_unit(key):
    """Extract physical unit from header key."""
    if match := units_regexp.match(key):
        return match.group("key"), match.group("units")
    return key, None
