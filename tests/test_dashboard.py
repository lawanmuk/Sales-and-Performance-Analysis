"""Smoke test: the dashboard renders on the real data without errors."""

from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = Path(__file__).resolve().parents[1] / "app" / "dashboard.py"


@pytest.fixture(scope="module")
def app():
    return AppTest.from_file(str(APP), default_timeout=180).run()


def test_renders_without_errors(app):
    assert not app.exception


def test_has_all_tabs(app):
    assert [t.label for t in app.tabs] == [
        "Overview",
        "Products",
        "Customers",
        "Geography",
        "Shipping",
        "Forecast",
    ]


def test_kpi_tiles_show_full_totals(app):
    tiles = {m.label: m.value for m in app.metric}
    assert tiles["Total sales"] == "$2,261,255"
    assert tiles["Orders"] == "4,922"


def test_clearing_a_filter_shows_a_warning_not_a_crash(app):
    app.sidebar.multiselect[0].set_value([]).run()
    assert not app.exception
    assert app.warning
