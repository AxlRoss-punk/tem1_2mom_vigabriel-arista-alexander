SET hive.local.time.zone=UTC;
SET hive.datetime.formatter=SIMPLE;
SELECT region,YEAR(order_date) AS anio,SUM(sales) AS ventas,SUM(profit) AS ganancia
FROM superstore_alexander_2mom.superstore
GROUP BY region,YEAR(order_date)
ORDER BY region,anio;
