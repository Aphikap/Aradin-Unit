"""Pure unit-conversion functions. No Flask imports here so tests stay fast."""

LENGTH_TO_METER = {
    "m": 1.0,
    "km": 1000.0,
    "cm": 0.01,
    "mm": 0.001,
    "inch": 0.0254,
    "foot": 0.3048,
    "yard": 0.9144,
    "mile": 1609.344,
}

WEIGHT_TO_KG = {
    "kg": 1.0,
    "g": 0.001,
    "mg": 0.000001,
    "lb": 0.45359237,
    "oz": 0.028349523125,
}

CATEGORIES = ("length", "weight", "temperature")


class ConversionError(ValueError):
    pass


def _factor_convert(table, src, dst, value):
    if src not in table:
        raise ConversionError(f"unknown unit: {src}")
    if dst not in table:
        raise ConversionError(f"unknown unit: {dst}")
    return value * table[src] / table[dst]


def _to_celsius(unit, value):
    if unit == "C":
        return value
    if unit == "F":
        return (value - 32.0) * 5.0 / 9.0
    if unit == "K":
        return value - 273.15
    raise ConversionError(f"unknown temperature unit: {unit}")


def _from_celsius(unit, celsius):
    if unit == "C":
        return celsius
    if unit == "F":
        return celsius * 9.0 / 5.0 + 32.0
    if unit == "K":
        return celsius + 273.15
    raise ConversionError(f"unknown temperature unit: {unit}")


def convert(category, src, dst, value):
    if category == "length":
        return _factor_convert(LENGTH_TO_METER, src, dst, value)
    if category == "weight":
        return _factor_convert(WEIGHT_TO_KG, src, dst, value)
    if category == "temperature":
        return _from_celsius(dst, _to_celsius(src, value))
    raise ConversionError(f"unknown category: {category}")


def units_for(category):
    if category == "length":
        return list(LENGTH_TO_METER)
    if category == "weight":
        return list(WEIGHT_TO_KG)
    if category == "temperature":
        return ["C", "F", "K"]
    raise ConversionError(f"unknown category: {category}")
