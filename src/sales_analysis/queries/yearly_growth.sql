-- Sales per year and growth on the previous year, using a window function.
WITH yearly AS (
    SELECT YEAR(order_date) AS year, SUM(sales) AS total_sales
    FROM sales
    GROUP BY year
)
SELECT
    year,
    ROUND(total_sales, 2) AS total_sales,
    ROUND(100 * (total_sales / LAG(total_sales) OVER (ORDER BY year) - 1), 1) AS growth_pct
FROM yearly
ORDER BY year;
