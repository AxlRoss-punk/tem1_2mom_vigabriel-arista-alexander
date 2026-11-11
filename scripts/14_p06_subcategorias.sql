SET hive.local.time.zone=UTC;
SET hive.datetime.formatter=SIMPLE;

WITH clasificado AS (
 SELECT *, CASE WHEN discount=0 THEN 'Sin descuento' WHEN discount<=0.20 THEN 'Bajo'
 WHEN discount<=0.50 THEN 'Medio' ELSE 'Alto' END AS banda FROM superstore_alexander_2mom.superstore
), grupos AS (
 SELECT banda,category,sub_category,COUNT(*) AS n,SUM(sales) AS ventas,SUM(profit) AS ganancia,
 COUNT(CASE WHEN profit<0 THEN 1 END) AS perdidas,
 SUM(CASE WHEN profit<0 THEN -profit ELSE 0 END) AS perdida_bruta,
 ROUND(100.0*COUNT(CASE WHEN profit<=0 THEN 1 END)/COUNT(*),4) AS pct_no_rentables,
 ROUND(100.0*SUM(profit)/SUM(sales),4) AS margen_pct
 FROM clasificado GROUP BY banda,category,sub_category
)
SELECT *,DENSE_RANK() OVER(PARTITION BY banda ORDER BY perdida_bruta DESC) AS rk_afectacion
FROM grupos ORDER BY banda,rk_afectacion,category,sub_category;

