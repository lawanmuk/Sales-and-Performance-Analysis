-- The 10 best selling products, ranked within the whole store and within their category.
WITH product_sales AS (
    SELECT category, product_name, SUM(sales) AS total_sales
    FROM sales
    GROUP BY category, product_name
)
SELECT
    RANK() OVER (ORDER BY total_sales DESC)                         AS overall_rank,
    RANK() OVER (PARTITION BY category ORDER BY total_sales DESC)   AS rank_in_category,
    category,
    product_name,
    ROUND(total_sales, 2)                                           AS total_sales
FROM product_sales
QUALIFY overall_rank <= 10
ORDER BY overall_rank;
