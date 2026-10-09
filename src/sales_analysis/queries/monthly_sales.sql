-- Sales for every month, plus a 3 month moving average.
WITH monthly AS (
    SELECT DATE_TRUNC('month', order_date) AS month, SUM(sales) AS total_sales
    FROM sales
    GROUP BY month
)
SELECT
    month,
    ROUND(total_sales, 2) AS total_sales,
    ROUND(AVG(total_sales) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2)
        AS moving_avg_3m
FROM monthly
ORDER BY month;
