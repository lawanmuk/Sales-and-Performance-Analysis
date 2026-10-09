"""Run the SQL versions of the key metrics with DuckDB.

The .sql files live in the ``queries`` folder next to this module, so they can
also be opened and run in any SQL tool that reads CSV (DuckDB CLI, DBeaver...).
"""

from importlib import resources
from pathlib import Path

import pandas as pd

QUERY_DIR = resources.files("sales_analysis") / "queries"
VIEW_FILE = "_sales_view.sql"


def list_queries() -> list[str]:
    """Names of the available queries (file names without .sql)."""
    return sorted(
        f.name.removesuffix(".sql")
        for f in QUERY_DIR.iterdir()
        if f.name.endswith(".sql") and f.name != VIEW_FILE
    )


def read_query(name: str) -> str:
    """The SQL text of query ``name``."""
    if name not in list_queries():
        raise ValueError(f"Unknown query '{name}'. Choose from: {', '.join(list_queries())}")
    return (QUERY_DIR / f"{name}.sql").read_text(encoding="utf-8")


def connect(csv_path: str | Path):
    """An in-memory DuckDB connection with a clean ``sales`` view over the CSV."""
    import duckdb  # imported here so the rest of the package works without it

    con = duckdb.connect()
    path = Path(csv_path).resolve().as_posix().replace("'", "''")
    view_sql = (QUERY_DIR / VIEW_FILE).read_text(encoding="utf-8")
    con.execute(view_sql.replace("{csv_path}", path))
    return con


def run_query(name: str, csv_path: str | Path) -> pd.DataFrame:
    """Run query ``name`` against the CSV and return the result as a DataFrame."""
    with connect(csv_path) as con:
        return con.execute(read_query(name)).df()
