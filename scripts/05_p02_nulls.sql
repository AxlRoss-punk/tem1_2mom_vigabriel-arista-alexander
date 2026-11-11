-- Pregunta 2: cantidad de NULL por cada una de las 21 columnas.
WITH nulos AS (
  SELECT
    COUNT(*) - COUNT(row_id) AS row_id,
    COUNT(*) - COUNT(order_id) AS order_id,
    COUNT(*) - COUNT(order_date) AS order_date,
    COUNT(*) - COUNT(ship_date) AS ship_date,
    COUNT(*) - COUNT(ship_mode) AS ship_mode,
    COUNT(*) - COUNT(customer_id) AS customer_id,
    COUNT(*) - COUNT(customer_name) AS customer_name,
    COUNT(*) - COUNT(segment) AS segment,
    COUNT(*) - COUNT(country) AS country,
    COUNT(*) - COUNT(city) AS city,
    COUNT(*) - COUNT(state) AS state,
    COUNT(*) - COUNT(postal_code) AS postal_code,
    COUNT(*) - COUNT(region) AS region,
    COUNT(*) - COUNT(product_id) AS product_id,
    COUNT(*) - COUNT(category) AS category,
    COUNT(*) - COUNT(sub_category) AS sub_category,
    COUNT(*) - COUNT(product_name) AS product_name,
    COUNT(*) - COUNT(sales) AS sales,
    COUNT(*) - COUNT(quantity) AS quantity,
    COUNT(*) - COUNT(discount) AS discount,
    COUNT(*) - COUNT(profit) AS profit
  FROM superstore_alexander_2mom.superstore
)
SELECT orden, columna, cantidad_null
FROM nulos
LATERAL VIEW STACK(21,
  1, 'row_id', row_id,
  2, 'order_id', order_id,
  3, 'order_date', order_date,
  4, 'ship_date', ship_date,
  5, 'ship_mode', ship_mode,
  6, 'customer_id', customer_id,
  7, 'customer_name', customer_name,
  8, 'segment', segment,
  9, 'country', country,
  10, 'city', city,
  11, 'state', state,
  12, 'postal_code', postal_code,
  13, 'region', region,
  14, 'product_id', product_id,
  15, 'category', category,
  16, 'sub_category', sub_category,
  17, 'product_name', product_name,
  18, 'sales', sales,
  19, 'quantity', quantity,
  20, 'discount', discount,
  21, 'profit', profit
) s AS orden, columna, cantidad_null
ORDER BY orden;
