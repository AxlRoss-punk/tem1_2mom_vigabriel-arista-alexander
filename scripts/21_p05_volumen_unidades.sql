-- Complemento de P5: volumen fisico en unidades, ademas del ranking por importe.
WITH producto AS (
 SELECT category,product_id,MIN(product_name) AS product_name,
 SUM(quantity) AS unidades,SUM(sales) AS ventas,SUM(profit) AS ganancia
 FROM superstore_alexander_2mom.superstore GROUP BY category,product_id
), ordenado AS (
 SELECT *,ROW_NUMBER() OVER(ORDER BY unidades DESC,product_id) AS posicion
 FROM producto
)
SELECT posicion,category,product_id,product_name,unidades,ventas,ganancia
FROM ordenado WHERE posicion<=5 ORDER BY posicion;
