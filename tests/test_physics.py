import pytest
from pint import UnitRegistry
from pygi.physics import unit_list

ureg = UnitRegistry()

def test_unit_list_understood_by_pint():
    """
    Ensure all units in unit_list are understood by pint.
    """
    for u in unit_list:
        assert ureg(u).dimensionality == ureg('meter').dimensionality
