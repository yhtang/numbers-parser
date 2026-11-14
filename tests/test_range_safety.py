import pytest

from numbers_parser.exceptions import UnsupportedError
from numbers_parser.formula import Formula
from numbers_parser.xrefs import CellRange


class Endpoint(CellRange):
    def __init__(self, target, text, invalid=False):
        self.to_table_id = target
        self.text = text
        self._ref_error = invalid

    def __str__(self):
        return self.text


def render(start, end):
    formula = Formula(None, None, 0, 0)
    formula.push(start)
    formula.push(end)
    formula.range()
    return str(formula)


def test_same_target_keeps_full_sheet_and_table_prefix():
    assert render(Endpoint(1, "Other::Values::A1"), Endpoint(1, "Other::Values::A2")) == \
        "Other::Values::A1:A2"
    assert render(Endpoint(1, "A1"), Endpoint(1, "A2")) == "A1:A2"


@pytest.mark.parametrize("start,end", [
    (Endpoint(1, "Values::A1"), Endpoint(2, "OtherData::A2")),
    # Equal display names are not evidence of equal target identities.
    (Endpoint(1, "Values::A1"), Endpoint(2, "Values::A2")),
    (Endpoint(1, "A1", invalid=True), Endpoint(1, "A2")),
    (Endpoint(1, "A1"), "INDEX(A1:A2,1)"),
    (Endpoint(1, "Values::A1"), Endpoint(1, "A2")),
])
def test_unidentified_or_conflicting_endpoints_refuse(start, end):
    with pytest.raises(UnsupportedError):
        render(start, end)
