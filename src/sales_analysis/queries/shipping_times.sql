-- Days from order to shipping per ship mode, one row per order (not per line).
WITH orders AS (
    SELECT DISTINCT order_id, ship_mode, DATEDIFF('day', order_date, ship_date) AS ship_days
    FROM sales
)
SELECT
    ship_mode,
    COUNT(*)                    AS orders,
    ROUND(AVG(ship_days), 2)    AS avg_days,
    MEDIAN(ship_days)           AS median_days,
    MAX(ship_days)              AS max_days
FROM orders
GROUP BY ship_mode
ORDER BY avg_days;
