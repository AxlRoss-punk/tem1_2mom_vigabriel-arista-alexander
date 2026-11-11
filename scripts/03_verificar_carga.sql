-- Pregunta 1. Comprobaciones de carga; solo lectura.
SELECT 'superstore_raw' AS tabla, COUNT(*) AS registros
FROM superstore_alexander_2mom.superstore_raw
UNION ALL
SELECT 'superstore' AS tabla, COUNT(*) AS registros
FROM superstore_alexander_2mom.superstore;

DESCRIBE superstore_alexander_2mom.superstore;

SELECT row_id, order_date, ship_date, postal_code, product_name,
       sales, quantity, discount, profit
FROM superstore_alexander_2mom.superstore
WHERE row_id IN (1, 2, 3, 17)
ORDER BY row_id;

SELECT row_id, postal_code, city, state
FROM superstore_alexander_2mom.superstore
WHERE postal_code = '05408'
ORDER BY row_id
LIMIT 3;
