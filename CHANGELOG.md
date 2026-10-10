# Changelog

## 1.0.0 (2026-10-10)

First full release, built over a one week sprint.

### Added
- Installable package (`pyproject.toml`) with the `sales-analysis` command: `run`, `summary`, `forecast` and `sql`.
- Streamlit dashboard with sidebar filters, KPI tiles against the previous period, six tabs and CSV download.
- Eight DuckDB SQL queries that match the pandas results.
- Six month forecast using Holt-Winters, chosen by a backtest against seasonal naive, with an 80% range.
- RFM customer segments, Pareto analysis, shipping times, seasonality heatmap and a state map.
- 55 pytest tests, ruff linting, pre-commit hooks and GitHub Actions CI on Ubuntu and Windows.

### Changed
- `requirements.txt` replaced by `pyproject.toml` as the single source of dependencies.
- Charts are reproducible: the same input gives byte identical PNG and HTML files.
- README rewritten with figures checked against the code.

### Fixed
- Order dates are parsed as day first (dd/mm/yyyy), so days and months are no longer swapped.
- Duplicate order lines are removed before any metric is calculated.
- A seaborn palette warning when a chart has more years than palette colours.
- Windows on ARM installs need 64-bit Python for numpy and pyarrow, now documented in the README.
