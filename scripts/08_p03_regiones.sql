SET hive.local.time.zone=UTC;
SET hive.datetime.formatter=SIMPLE;

WITH regional AS (
 SELECT region, SUM(sales) AS ventas, SUM(profit) AS ganancia
 FROM superstore_alexander_2mom.superstore GROUP BY region
)
SELECT region, ventas, ganancia, ROUND(100.0*ganancia/ventas,4) AS margen_pct,
 DENSE_RANK() OVER(ORDER BY ganancia DESC) AS rk_mejor,
 DENSE_RANK() OVER(ORDER BY ganancia ASC) AS rk_peor
FROM regional ORDER BY rk_mejor,region;

