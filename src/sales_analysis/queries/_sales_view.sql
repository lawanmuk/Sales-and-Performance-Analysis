-- Clean view over the raw CSV, used by every query.
-- Mirrors data.clean(): parses day-first dates, drops the duplicate order line
-- and adds Year, Month and ShipDays columns. The CSV path is filled in at runtime.
CREATE OR REPLACE VIEW sales AS
SELECT DISTINCT
    "Order ID"                               AS order_id,
    strptime("Order Date", '%d/%m/%Y')::DATE AS order_date,
    strptime("Ship Date",  '%d/%m/%Y')::DATE AS ship_date,
    "Ship Mode"                              AS ship_mode,
    "Customer ID"                            AS customer_id,
    "Customer Name"                          AS customer_name,
    "Segment"                                AS segment,
    "City"                                   AS city,
    "State"                                  AS state,
    "Region"                                 AS region,
    "Product ID"                             AS product_id,
    "Category"                               AS category,
    "Sub-Category"                           AS sub_category,
    "Product Name"                           AS product_name,
    "Sales"                                  AS sales
FROM read_csv_auto('{csv_path}', header = true, all_varchar = true,
                   types = {'Sales': 'DOUBLE'});
