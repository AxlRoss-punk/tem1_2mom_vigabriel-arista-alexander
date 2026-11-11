SET hive.local.time.zone=UTC;
SET hive.datetime.formatter=SIMPLE;

WITH cliente AS (
 SELECT customer_id, MAX(customer_name) AS customer_name, MAX(order_date) AS ultima_compra,
 COUNT(DISTINCT order_id) AS frecuencia, SUM(sales) AS monetario
 FROM superstore_alexander_2mom.superstore GROUP BY customer_id
), medidas AS (
 SELECT *, MAX(ultima_compra) OVER() AS referencia,
 DATEDIFF(MAX(ultima_compra) OVER(),ultima_compra) AS recencia FROM cliente
), puntuaciones AS (
 SELECT *,
 NTILE(5) OVER(ORDER BY recencia DESC,customer_id) AS r,
 NTILE(5) OVER(ORDER BY frecuencia ASC,customer_id) AS f,
 NTILE(5) OVER(ORDER BY monetario ASC,customer_id) AS m
 FROM medidas
), resultado AS (
 SELECT *, CONCAT(CAST(r AS STRING),CAST(f AS STRING),CAST(m AS STRING)) AS rfm,
 CASE WHEN r>=4 AND f>=4 AND m>=4 THEN 'Alto valor'
 WHEN r<=2 AND (f>=3 OR m>=3) THEN 'En riesgo'
 WHEN f>=4 THEN 'Recurrentes'
 WHEN r>=4 AND f<=2 THEN 'Recientes'
 ELSE 'Otros' END AS segmento
 FROM puntuaciones
)
SELECT segmento,COUNT(*) AS clientes,SUM(monetario) AS ventas,ROUND(AVG(recencia),2) AS recencia_media,ROUND(AVG(frecuencia),2) AS frecuencia_media FROM resultado GROUP BY segmento ORDER BY ventas DESC;

