-- The 10 customers with the highest total sales.
SELECT
    customer_id,
    customer_name,
    segment,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2)     AS total_sales
FROM sales
GROUP BY customer_id, customer_name, segment
ORDER BY total_sales DESC
LIMIT 10;
