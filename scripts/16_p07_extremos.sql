SET hive.local.time.zone=UTC;
SET hive.datetime.formatter=SIMPLE;

WITH mensual AS (
SELECT CONCAT(CAST(YEAR(order_date) AS STRING),'-',LPAD(CAST(MONTH(order_date) AS STRING),2,'0'),'-01') AS mes,
 SUM(sales) AS ventas,SUM(profit) AS ganancia
 FROM superstore_alexander_2mom.superstore GROUP BY YEAR(order_date),MONTH(order_date)
), limites AS (
 SELECT MIN(mes) AS inicio,MAX(mes) AS fin FROM mensual
), numeros AS (SELECT STACK(120,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119) AS n),
 calendario AS (
 SELECT ADD_MONTHS(l.inicio,n.n) AS mes FROM limites l CROSS JOIN numeros n
 WHERE ADD_MONTHS(l.inicio,n.n)<=l.fin
), serie AS (
 SELECT c.mes,COALESCE(m.ventas,0) AS ventas,COALESCE(m.ganancia,0) AS ganancia
 FROM calendario c LEFT JOIN mensual m ON c.mes=m.mes
), ventanas AS (
 SELECT *,
 LAG(ventas,1) OVER(ORDER BY mes) AS ventas_ant,
 LAG(ventas,12) OVER(ORDER BY mes) AS ventas_interanual,
 LAG(ganancia,1) OVER(ORDER BY mes) AS ganancia_ant,
 LAG(ganancia,12) OVER(ORDER BY mes) AS ganancia_interanual,
 CASE WHEN COUNT(*) OVER(ORDER BY mes ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)=3
 THEN AVG(ventas) OVER(ORDER BY mes ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) END AS media_ventas,
 CASE WHEN COUNT(*) OVER(ORDER BY mes ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)=3
 THEN AVG(ganancia) OVER(ORDER BY mes ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) END AS media_ganancia,
 ROW_NUMBER() OVER(ORDER BY ventas DESC,mes) AS rk_mayor,
 ROW_NUMBER() OVER(ORDER BY ventas ASC,mes) AS rk_menor
 FROM serie
), resultado AS (
 SELECT mes,ventas,ganancia,
 CASE WHEN ventas_ant<>0 THEN ROUND(100.0*(ventas-ventas_ant)/ventas_ant,4) END AS var_mes_pct,
 CASE WHEN ventas_interanual<>0 THEN ROUND(100.0*(ventas-ventas_interanual)/ventas_interanual,4) END AS var_anio_pct,
 CASE WHEN ganancia_ant<>0 THEN ROUND(100.0*(ganancia-ganancia_ant)/ABS(ganancia_ant),4) END AS var_gan_mes_pct,
 CASE WHEN ganancia_interanual<>0 THEN ROUND(100.0*(ganancia-ganancia_interanual)/ABS(ganancia_interanual),4) END AS var_gan_anio_pct,
 ROUND(media_ventas,4) AS mm3_ventas,ROUND(media_ganancia,4) AS mm3_ganancia,rk_mayor,rk_menor
 FROM ventanas
)
SELECT * FROM resultado WHERE rk_mayor<=3 OR rk_menor<=3 ORDER BY ventas DESC,mes;

