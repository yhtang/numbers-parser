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


def test_missing_cross_table_target_does_not_become_local():
    from numbers_parser import Document, UnsupportedError

    doc = Document("tests/data/create-formulas.numbers")
    table = doc.sheets["Main Sheet"].tables["Reference Tests"]
    cell = table.cell("A2")
    assert cell.formula.startswith("SUM(Powers of Two::")
    nodes = doc._model.formula_ast(table._table_id)[cell._formula_id]
    target = next(node for node in nodes if node.HasField("AST_cross_table_reference_extra_info"))
    target.AST_cross_table_reference_extra_info.table_id.uuid_w0 ^= 1
    with pytest.raises(UnsupportedError):
        _ = cell.formula
