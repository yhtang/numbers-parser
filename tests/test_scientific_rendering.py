from decimal import Decimal

import pytest

from numbers_parser.formula import number_to_str


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1.23456789e-7, "0.000000123456789"),
        (1.23e-9, "0.00000000123"),
        (1.23e9, "1230000000.0"),
        (123.4, "123.4"),
        (0.0, "0.0"),
    ],
)
def test_number_to_str_preserves_observed_value(value, expected):
    assert Decimal(number_to_str(value)) == Decimal(expected)
