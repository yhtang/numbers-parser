from datetime import datetime

import pytest

from numbers_parser import Document, UnsupportedError


@pytest.mark.parametrize("variant", ["number", "formatted", "true", "false", "date", "text_true"])
def test_named_header_does_not_render_as_an_unrelated_literal(tmp_path, variant):
    doc = Document("tests/data/create-formulas.numbers")
    source = doc.sheets["Main Sheet"].tables["Reference Tests"]
    target = doc.sheets["Main Sheet"].tables["Extra Headers"]
    node = doc._model.formula_ast(source._table_id)[source.cell("A55")._formula_id][0]
    row = 1
    if variant == "formatted":
        target.set_cell_formatting("A2", "number", decimal_places=0)
    elif variant in {"true", "false"}:
        row = 3 if variant == "true" else 4
        node.AST_row.row = row - 54
    elif variant == "date":
        target.write("A2", datetime(2024, 2, 3, 14, 30))
    elif variant == "text_true":
        target.write("A4", "another")  # Keep the text header unique.
        target.write("A2", "TRUE")
    path = tmp_path / f"{variant}.numbers"
    doc.save(path)
    reopened = Document(path)
    target = reopened.sheets["Main Sheet"].tables["Extra Headers"]
    assert all(isinstance(target.cell(row, col).value, str) for col in (1, 2))
    cell = reopened.sheets["Main Sheet"].tables["Reference Tests"].cell("A55")
    assert cell.formula.startswith("COUNTA(")  # Existing public rendering is unchanged.
    with pytest.raises(UnsupportedError, match="named header reference"):
        _ = cell.formula_without_header_names


def test_coordinate_formula_stays_available():
    doc = Document("tests/data/test-10.numbers")
    assert doc.sheets[0].tables[0].cell("B2").formula == "A1+A2"
    assert doc.sheets[0].tables[0].cell("B2").formula_without_header_names == "A1+A2"


def test_grouping_probe_does_not_hide_operational_errors(monkeypatch):
    doc = Document("tests/data/test-10.numbers")
    table = doc.sheets[0].tables[0]

    class UnavailableObjects:
        def __getitem__(self, _key):
            raise OSError("storage unavailable")

    monkeypatch.setattr(doc._model, "objects", UnavailableObjects())
    with pytest.raises(OSError, match="storage unavailable"):
        _ = table.has_grouping
