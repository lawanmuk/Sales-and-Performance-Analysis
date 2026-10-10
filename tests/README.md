# Tests

`fixtures/sample.csv` is a tiny hand-made dataset (8 rows, one of them a
duplicate) so every expected number in the tests can be checked by hand:

| | Value |
|---|---|
| Rows after removing the duplicate | 7 |
| Total sales | 2,750 |
| Sales 2017 / 2018 | 1,100 / 1,650 (+50%) |
| Technology / Furniture / Office Supplies | 1,700 / 900 / 150 |
| West / South / Central / East | 900 / 950 / 600 / 300 |
| Orders / customers | 6 / 4 |

Run them with `pytest`.
