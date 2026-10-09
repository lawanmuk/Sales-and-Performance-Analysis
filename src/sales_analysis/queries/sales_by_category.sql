-- Total sales per category and its share of all sales.
SELECT
    category,
    ROUND(SUM(sales), 2)                                   AS total_sales,
    ROUND(100 * SUM(sales) / SUM(SUM(sales)) OVER (), 1)   AS share_pct
FROM sales
GROUP BY category
ORDER BY total_sales DESC;
