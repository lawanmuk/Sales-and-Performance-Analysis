-- Sales, orders and average order value per region.
SELECT
    region,
    ROUND(SUM(sales), 2)                              AS total_sales,
    COUNT(DISTINCT order_id)                          AS orders,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2)   AS avg_order_value
FROM sales
GROUP BY region
ORDER BY total_sales DESC;
