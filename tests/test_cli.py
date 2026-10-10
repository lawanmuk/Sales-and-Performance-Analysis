import pytest

from sales_analysis import plots
from sales_analysis.cli import main


def test_summary_prints_totals_and_insights(sample_csv, capsys):
    main(["summary", "--data", str(sample_csv)])
    out = capsys.readouterr().out
    assert "Total sales:      $2,750" in out
    assert "Technology is the top category" in out
    assert "Sales grew 50.0% in 2018" in out


def test_run_saves_charts_and_skips_what_the_data_cannot_support(
    sample_csv, tmp_path, capsys, monkeypatch
):
    monkeypatch.setenv("MPLBACKEND", "Agg")
    main(["run", "--data", str(sample_csv), "--output", str(tmp_path)])
    out = capsys.readouterr().out
    saved = list(tmp_path.iterdir())
    # The sample has only 2 years, too short to forecast, so that chart is skipped
    assert "Skipped sales_forecast" in out
    assert len(saved) == len(plots.ALL_CHARTS) - 1


def test_sql_list(capsys):
    pytest.importorskip("duckdb")
    main(["sql", "--list"])
    assert "top_products" in capsys.readouterr().out


def test_unknown_command_exits():
    with pytest.raises(SystemExit):
        main(["nope"])
