SET hive.local.time.zone=UTC;
SET hive.datetime.formatter=SIMPLE;

WITH producto AS (
 SELECT product_id, SUM(sales) AS ventas,SUM(profit) AS ganancia FROM superstore_alexander_2mom.superstore GROUP BY product_id
), aportes AS (
 SELECT 'ventas' AS analisis,product_id,ventas AS valor FROM producto
 UNION ALL SELECT 'ganancia_neta' AS analisis,product_id,ganancia AS valor FROM producto
), acumulados AS (
 SELECT *, ROW_NUMBER() OVER(PARTITION BY analisis ORDER BY valor DESC,product_id) AS puesto,
 SUM(valor) OVER(PARTITION BY analisis) AS total,
 SUM(valor) OVER(PARTITION BY analisis ORDER BY valor DESC,product_id
 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS acumulado
 FROM aportes
), resultado AS (
 SELECT *,
 ROUND(100.0*valor/total,4) AS participacion_pct,
 ROUND(100.0*acumulado/total,4) AS acumulado_pct,
 MIN(CASE WHEN acumulado>=0.8*total THEN puesto END) OVER(PARTITION BY analisis) AS n80
 FROM acumulados
)
SELECT analisis,COUNT(*) AS productos,MAX(total) AS total,MAX(n80) AS productos_80,
 ROUND(100.0*MAX(n80)/COUNT(*),4) AS pct_productos,
 SUM(CASE WHEN puesto<=n80 THEN valor ELSE 0 END) AS aporte_80,
 ROUND(100.0*SUM(CASE WHEN puesto<=n80 THEN valor ELSE 0 END)/MAX(total),4) AS pct_alcanzado,
 COUNT(CASE WHEN valor<0 THEN 1 END) AS productos_negativos
FROM resultado GROUP BY analisis ORDER BY analisis;

