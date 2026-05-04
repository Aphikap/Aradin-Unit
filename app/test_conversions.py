import math

import pytest

from conversions import ConversionError, convert, units_for


def test_length_meter_to_kilometer():
    assert convert("length", "m", "km", 1000) == 1.0


def test_length_inch_to_centimeter():
    assert convert("length", "inch", "cm", 1) == pytest.approx(2.54)


def test_length_mile_to_meter():
    assert convert("length", "mile", "m", 1) == pytest.approx(1609.344)


def test_weight_kg_to_pound():
    assert convert("weight", "kg", "lb", 1) == pytest.approx(2.2046226218, rel=1e-6)


def test_weight_oz_to_g():
    assert convert("weight", "oz", "g", 1) == pytest.approx(28.349523125)


def test_temperature_c_to_f():
    assert convert("temperature", "C", "F", 0) == pytest.approx(32.0)
    assert convert("temperature", "C", "F", 100) == pytest.approx(212.0)


def test_temperature_f_to_k():
    assert convert("temperature", "F", "K", 32) == pytest.approx(273.15)


def test_temperature_round_trip():
    for unit in ("C", "F", "K"):
        round_tripped = convert(
            "temperature", "C", unit, convert("temperature", unit, "C", 25)
        )
        assert math.isclose(round_tripped, 25, rel_tol=1e-9)


def test_same_unit_returns_input():
    assert convert("length", "m", "m", 42.0) == 42.0
    assert convert("temperature", "C", "C", -10.0) == -10.0


def test_unknown_category_raises():
    with pytest.raises(ConversionError):
        convert("volume", "L", "mL", 1)


def test_unknown_unit_raises():
    with pytest.raises(ConversionError):
        convert("length", "parsec", "m", 1)


def test_units_for_returns_expected():
    assert "m" in units_for("length")
    assert "kg" in units_for("weight")
    assert units_for("temperature") == ["C", "F", "K"]
