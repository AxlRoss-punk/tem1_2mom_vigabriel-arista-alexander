SET hive.local.time.zone=UTC;
SET hive.datetime.formatter=SIMPLE;

WITH anual AS (
 SELECT region, YEAR(order_date) AS anio, SUM(sales) AS ventas, SUM(profit) AS ganancia
 FROM superstore_alexander_2mom.superstore GROUP BY region, YEAR(order_date)
), anterior AS (
 SELECT *, LAG(ventas) OVER(PARTITION BY region ORDER BY anio) AS ventas_ant,
 LAG(ganancia) OVER(PARTITION BY region ORDER BY anio) AS ganancia_ant
 FROM anual
), resultado AS (
 SELECT region, anio, ventas, ganancia,
 ROUND(100.0*ganancia/ventas,4) AS margen_pct,
 CASE WHEN ventas_ant<>0 THEN ROUND(100.0*(ventas-ventas_ant)/ventas_ant,4) END AS var_ventas_pct,
 CASE WHEN ganancia_ant<>0 THEN ROUND(100.0*(ganancia-ganancia_ant)/ABS(ganancia_ant),4) END AS var_ganancia_pct,
 DENSE_RANK() OVER(PARTITION BY anio ORDER BY ganancia DESC) AS rk_ganancia
 FROM anterior
)
SELECT * FROM resultado ORDER BY region,anio;

