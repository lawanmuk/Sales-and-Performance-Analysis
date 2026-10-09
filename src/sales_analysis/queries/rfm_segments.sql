-- RFM scores per customer with NTILE, then customers and sales per segment.
-- Scores run 1 (worst) to 4 (best), like metrics.rfm() in Python.
-- Counts can differ from Python by a few customers: when several customers
-- tie on a value, NTILE and pandas put them into quartiles in a different order.
WITH snapshot AS (
    SELECT MAX(order_date) + INTERVAL 1 DAY AS day FROM sales
),
customers AS (
    SELECT
        customer_id,
        DATEDIFF('day', MAX(order_date), (SELECT day FROM snapshot)) AS recency,
        COUNT(DISTINCT order_id)                                     AS frequency,
        SUM(sales)                                                   AS monetary
    FROM sales
    GROUP BY customer_id
),
scored AS (
    SELECT *,
        NTILE(4) OVER (ORDER BY recency DESC)  AS r,
        NTILE(4) OVER (ORDER BY frequency)     AS f,
        NTILE(4) OVER (ORDER BY monetary)      AS m
    FROM customers
),
segmented AS (
    SELECT *,
        CASE
            WHEN r >= 3 AND f >= 3 AND m >= 3 THEN 'Champions'
            WHEN f >= 3 AND r >= 2            THEN 'Loyal'
            WHEN f >= 3                       THEN 'At Risk'
            WHEN r >= 3                       THEN 'Needs Attention'
            WHEN r = 2                        THEN 'At Risk'
            ELSE 'Lost'
        END AS segment
    FROM scored
)
SELECT
    segment,
    COUNT(*)                                                AS customers,
    ROUND(SUM(monetary), 2)                                 AS total_sales,
    ROUND(100 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 1) AS share_pct
FROM segmented
GROUP BY segment
ORDER BY total_sales DESC;
