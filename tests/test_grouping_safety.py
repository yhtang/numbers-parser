from numbers_parser import Document, UnsupportedError
import pytest


def test_grouping_flag_checks_legacy_owner_after_save(tmp_path):
    doc = Document("tests/data/test-categories.numbers")
    table = doc.sheets[0].tables["Categories"]
    assert table.has_grouping is True
    doc._model.objects[table._table_id].ClearField("category_owner")
    path = tmp_path / "legacy-owner.numbers"
    doc.save(path)
    reopened = Document(path).sheets[0].tables["Categories"]
    assert reopened.categorized_data() is None  # The legacy decoder misses it.
    assert reopened.has_grouping is True


def test_grouping_flag_rejects_missing_state():
    doc = Document("tests/data/test-10.numbers")
    table = doc.sheets[0].tables[0]
    model = doc._model.objects[table._table_id]
    model.ClearField("category_owner")
    model.ClearField("category_owner_deprecated")
    with pytest.raises(UnsupportedError):
        _ = table.has_grouping


def test_grouping_flag_checks_both_owners():
    doc = Document("tests/data/test-categories.numbers")
    table = doc.sheets[0].tables["Categories"]
    model = doc._model.objects[table._table_id]
    model.category_owner_deprecated.group_by[0].is_enabled = False
    assert table.has_grouping is True  # Current owner still has grouping enabled.
    model.category_owner_deprecated.group_by[0].is_enabled = True
    owner = doc._model.objects[model.category_owner.identifier]
    doc._model.objects[owner.group_by[0].identifier].is_enabled = False
    assert table.has_grouping is True  # Legacy owner still has grouping enabled.
