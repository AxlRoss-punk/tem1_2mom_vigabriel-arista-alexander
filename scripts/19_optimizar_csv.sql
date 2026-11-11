SET hive.local.time.zone=UTC;
SET hive.datetime.formatter=SIMPLE;
SELECT region,
 YEAR(TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(order_date,'M/d/yyyy')))) AS anio,
 SUM(CAST(sales AS DECIMAL(12,4))) AS ventas,
 SUM(CAST(profit AS DECIMAL(12,4))) AS ganancia
FROM superstore_alexander_2mom.superstore_raw
GROUP BY region,YEAR(TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(order_date,'M/d/yyyy'))))
ORDER BY region,anio;
