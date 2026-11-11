SET hive.local.time.zone=UTC;
SET hive.datetime.formatter=SIMPLE;

WITH clasificado AS (
 SELECT *, CASE WHEN discount=0 THEN 'Sin descuento' WHEN discount<=0.20 THEN 'Bajo'
 WHEN discount<=0.50 THEN 'Medio' ELSE 'Alto' END AS banda FROM superstore_alexander_2mom.superstore
), resultado AS (
 SELECT banda, COUNT(*) AS n, SUM(sales) AS ventas, SUM(profit) AS ganancia,
 ROUND(100.0*SUM(profit)/SUM(sales),4) AS margen_pct,
 COUNT(CASE WHEN profit<0 THEN 1 END) AS perdidas,
 COUNT(CASE WHEN profit<=0 THEN 1 END) AS no_rentables,
 ROUND(100.0*COUNT(CASE WHEN profit<0 THEN 1 END)/COUNT(*),4) AS pct_perdidas,
 ROUND(100.0*COUNT(CASE WHEN profit<=0 THEN 1 END)/COUNT(*),4) AS pct_no_rentables,
 ROUND(AVG(discount),4) AS desc_prom
 FROM clasificado GROUP BY banda
)
SELECT banda,n,ventas,ganancia,margen_pct,pct_no_rentables,desc_prom FROM resultado ORDER BY desc_prom;

