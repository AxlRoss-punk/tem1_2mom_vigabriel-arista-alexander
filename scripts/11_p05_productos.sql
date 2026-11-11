SET hive.local.time.zone=UTC;
SET hive.datetime.formatter=SIMPLE;

WITH producto AS (
 SELECT category, product_id, MIN(product_name) AS product_name,
 COUNT(DISTINCT product_name) AS variantes_nombre,
 SUM(sales) AS ventas, SUM(profit) AS ganancia, SUM(quantity) AS unidades
 FROM superstore_alexander_2mom.superstore GROUP BY category, product_id
), margenes AS (
 SELECT *, 100.0*ganancia/ventas AS margen FROM producto
), resultado AS (
 SELECT *, ROUND(margen,4) AS margen_pct,
 RANK() OVER(PARTITION BY category ORDER BY ganancia DESC) AS rank_categoria,
 DENSE_RANK() OVER(PARTITION BY category ORDER BY ganancia DESC) AS dense_categoria,
 ROW_NUMBER() OVER(PARTITION BY category ORDER BY ganancia DESC,product_id) AS top_categoria,
 ROW_NUMBER() OVER(ORDER BY ventas DESC,product_id) AS top_ventas,
 ROW_NUMBER() OVER(ORDER BY ganancia ASC,product_id) AS peor_ganancia,
 ROW_NUMBER() OVER(ORDER BY margen ASC,product_id) AS peor_margen,
 SUM(ganancia) OVER(PARTITION BY category ORDER BY ganancia DESC,product_id
 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS ganancia_acumulada,
 SUM(ventas) OVER(PARTITION BY category ORDER BY ganancia DESC,product_id
 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS ventas_acumuladas
 FROM margenes
)
SELECT category,product_id,product_name,variantes_nombre,ventas,ganancia,unidades,margen_pct,rank_categoria,dense_categoria,top_categoria,top_ventas,peor_ganancia,peor_margen,ganancia_acumulada,ventas_acumuladas FROM resultado ORDER BY category,top_categoria;

