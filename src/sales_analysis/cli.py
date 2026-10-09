"""Command line entry point.

    sales-analysis run                  # build every chart into visuals/
    sales-analysis run --show           # also open each chart
    sales-analysis summary              # print headline numbers
    sales-analysis forecast             # backtest models and forecast 6 months
    sales-analysis sql --list           # list the SQL queries
    sales-analysis sql top_products     # run one SQL query with DuckDB
"""

import argparse
from pathlib import Path

import pandas as pd

from sales_analysis import forecast, metrics, plots, sql
from sales_analysis.data import load_data

DEFAULT_DATA = Path("data/train.csv")
DEFAULT_OUTPUT = Path("visuals")


MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def _print_summary(df) -> None:
    s = metrics.summary(df)
    print(f"Orders from {s['first_order']} to {s['last_order']}")
    print(f"Total sales:      ${s['total_sales']:,.0f}")
    print(f"Orders:           {s['orders']:,}")
    print(f"Customers:        {s['customers']:,}")
    print(f"Avg order value:  ${s['avg_order_value']:,.2f}")

    i = metrics.insights(df)
    print("\nKey insights")
    print(f"- {i['top_category']} is the top category "
          f"({i['top_category_share']:.0f}% of sales).")
    print(f"- {MONTHS[i['best_month'] - 1]} is the best month, "
          f"{i['best_month_vs_avg']:.0f}% above the monthly average.")
    print(f"- Sales grew {i['latest_growth']:.1f}% in {i['latest_year']}.")
    print(f"- The {i['top_region']} region leads with "
          f"{i['top_region_share']:.0f}% of sales.")
    print(f"- {i['top_segment']} customers bring in "
          f"{i['top_segment_share']:.0f}% of sales.")
    print(f"- {i['products_for_80pct']:.0f}% of products make up 80% of sales.")
    print(f"- Champion customers (RFM) bring in {i['champions_share']:.0f}% of sales.")
    print(f"- Standard Class orders take {i['standard_ship_days']:.1f} days "
          f"to ship on average.")


def cmd_run(args) -> None:
    df = load_data(args.data)
    args.output.mkdir(parents=True, exist_ok=True)
    for chart in plots.ALL_CHARTS:
        path = chart(df, args.output, show=args.show)
        print(f"Saved {path}")


def cmd_summary(args) -> None:
    _print_summary(load_data(args.data))


def cmd_forecast(args) -> None:
    result = forecast.run_forecast(load_data(args.data), horizon=args.months)

    print("Backtest: models trained on 2015-2017, scored on 2018")
    print(result.backtest.to_string(index=False, float_format=lambda x: f"{x:,.1f}"))
    print(f"\nBest model: {result.model}\n")

    table = result.forecast.copy()
    table["Month"] = table["Month"].dt.strftime("%b %Y")
    for col in ["Forecast", "Lower", "Upper"]:
        table[col] = table[col].map(lambda x: f"${x:,.0f}")
    print(f"Forecast with 80% range ({len(table)} months)")
    print(table.to_string(index=False))


def cmd_sql(args) -> None:
    if args.list or not args.query:
        print("Available queries:")
        for name in sql.list_queries():
            print(f"  {name}")
        return
    if args.show_sql:
        print(sql.read_query(args.query))
    with pd.option_context("display.width", 140, "display.max_columns", None):
        print(sql.run_query(args.query, args.data).to_string(index=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sales-analysis",
        description="Sales performance analysis of the Superstore dataset.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="build every chart")
    run.add_argument("--data", type=Path, default=DEFAULT_DATA,
                     help=f"path to the CSV (default: {DEFAULT_DATA})")
    run.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                     help=f"folder for the charts (default: {DEFAULT_OUTPUT})")
    run.add_argument("--show", action="store_true",
                     help="open each chart after saving it")
    run.set_defaults(func=cmd_run)

    summary = sub.add_parser("summary", help="print headline numbers")
    summary.add_argument("--data", type=Path, default=DEFAULT_DATA,
                         help=f"path to the CSV (default: {DEFAULT_DATA})")
    summary.set_defaults(func=cmd_summary)

    fc = sub.add_parser("forecast", help="backtest models and forecast monthly sales")
    fc.add_argument("--data", type=Path, default=DEFAULT_DATA,
                    help=f"path to the CSV (default: {DEFAULT_DATA})")
    fc.add_argument("--months", type=int, default=6,
                    help="how many months ahead to forecast (default: 6)")
    fc.set_defaults(func=cmd_forecast)

    q = sub.add_parser("sql", help="run a SQL version of a metric with DuckDB")
    q.add_argument("query", nargs="?", help="query name, see --list")
    q.add_argument("--list", action="store_true", help="list the available queries")
    q.add_argument("--show-sql", action="store_true", help="print the SQL before the result")
    q.add_argument("--data", type=Path, default=DEFAULT_DATA,
                   help=f"path to the CSV (default: {DEFAULT_DATA})")
    q.set_defaults(func=cmd_sql)

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
