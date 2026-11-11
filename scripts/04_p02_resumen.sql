-- Pregunta 2: resumen de calidad. Solo lectura; SET afecta a esta sesión.
SET hive.local.time.zone=UTC;
SET hive.datetime.formatter=SIMPLE;

WITH analitica AS (
  SELECT
    COUNT(*) AS registros,
    COUNT(DISTINCT order_id) AS ordenes_unicas,
    COUNT(DISTINCT customer_id) AS clientes_unicos,
    COUNT(CASE WHEN
      row_id IS NULL OR order_id IS NULL OR order_date IS NULL
      OR ship_date IS NULL OR ship_mode IS NULL OR customer_id IS NULL
      OR customer_name IS NULL OR segment IS NULL OR country IS NULL
      OR city IS NULL OR state IS NULL OR postal_code IS NULL
      OR region IS NULL OR product_id IS NULL OR category IS NULL
      OR sub_category IS NULL OR product_name IS NULL OR sales IS NULL
      OR quantity IS NULL OR discount IS NULL OR profit IS NULL
      THEN 1 END) AS filas_con_null,
    COUNT(*) * 21 - (
      COUNT(row_id) + COUNT(order_id) + COUNT(order_date) + COUNT(ship_date)
      + COUNT(ship_mode) + COUNT(customer_id) + COUNT(customer_name)
      + COUNT(segment) + COUNT(country) + COUNT(city) + COUNT(state)
      + COUNT(postal_code) + COUNT(region) + COUNT(product_id)
      + COUNT(category) + COUNT(sub_category) + COUNT(product_name)
      + COUNT(sales) + COUNT(quantity) + COUNT(discount) + COUNT(profit)
    ) AS valores_null,
    COUNT(CASE WHEN order_date IS NULL OR ship_date IS NULL THEN 1 END)
      AS filas_fecha_null,
    COUNT(CASE WHEN sales <= 0 THEN 1 END) AS ventas_no_positivas,
    COUNT(CASE WHEN discount < 0 OR discount > 1 THEN 1 END)
      AS descuentos_fuera_rango,
    COUNT(CASE WHEN ship_date < order_date THEN 1 END)
      AS envios_anteriores,
    COUNT(CASE WHEN quantity <= 0 THEN 1 END) AS cantidades_no_positivas,
    COUNT(CASE WHEN postal_code RLIKE '^[0-9]{4}$' THEN 1 END)
      AS postales_cuatro_digitos,
    COUNT(CASE WHEN postal_code RLIKE '^0[0-9]+$' THEN 1 END)
      AS postales_cero_inicial,
    COUNT(CASE WHEN product_name <> TRIM(product_name) THEN 1 END)
      AS productos_espacios_ascii,
    -- El carácter entre comillas es un espacio no separable U+00A0.
    COUNT(CASE WHEN INSTR(product_name, ' ') > 0 THEN 1 END)
      AS productos_espacio_no_separable
  FROM superstore_alexander_2mom.superstore
), grupos_duplicados AS (
  SELECT row_id, COUNT(*) AS repeticiones
  FROM superstore_alexander_2mom.superstore
  WHERE row_id IS NOT NULL
  GROUP BY row_id
  HAVING COUNT(*) > 1
), duplicados AS (
  SELECT COUNT(*) AS identificadores_repetidos,
         COALESCE(SUM(repeticiones - 1), 0) AS filas_adicionales
  FROM grupos_duplicados
), fechas_origen AS (
  SELECT
    order_date, ship_date,
    FROM_UNIXTIME(UNIX_TIMESTAMP(TRIM(order_date), 'M/d/yyyy'), 'M/d/yyyy')
      AS pedido_reconvertido,
    FROM_UNIXTIME(UNIX_TIMESTAMP(TRIM(ship_date), 'M/d/yyyy'), 'M/d/yyyy')
      AS envio_reconvertido
  FROM superstore_alexander_2mom.superstore_raw
), flags_fechas AS (
  SELECT
    CASE WHEN order_date IS NULL OR pedido_reconvertido IS NULL
      OR pedido_reconvertido <> TRIM(order_date) THEN 1 ELSE 0 END
      AS pedido_invalido,
    CASE WHEN ship_date IS NULL OR envio_reconvertido IS NULL
      OR envio_reconvertido <> TRIM(ship_date) THEN 1 ELSE 0 END
      AS envio_invalido
  FROM fechas_origen
), fechas AS (
  SELECT COUNT(*) AS registros_origen,
    COUNT(CASE WHEN pedido_invalido = 1 THEN 1 END) AS pedidos_invalidos,
    COUNT(CASE WHEN envio_invalido = 1 THEN 1 END) AS envios_invalidos,
    COUNT(CASE WHEN pedido_invalido = 1 OR envio_invalido = 1 THEN 1 END)
      AS filas_fecha_invalida
  FROM flags_fechas
), totales AS (
  SELECT a.*, d.*, f.*
  FROM analitica a CROSS JOIN duplicados d CROSS JOIN fechas f
)
SELECT orden, indicador, valor
FROM totales
LATERAL VIEW STACK(20,
  1, 'registros_analiticos', registros,
  2, 'registros_origen', registros_origen,
  3, 'identificadores_fila_duplicados', identificadores_repetidos,
  4, 'filas_duplicadas_adicionales', filas_adicionales,
  5, 'ordenes_unicas', ordenes_unicas,
  6, 'clientes_unicos', clientes_unicos,
  7, 'filas_con_algun_null', filas_con_null,
  8, 'valores_null_21_columnas', valores_null,
  9, 'pedidos_fecha_invalida_origen', pedidos_invalidos,
  10, 'envios_fecha_invalida_origen', envios_invalidos,
  11, 'filas_fecha_invalida_origen', filas_fecha_invalida,
  12, 'filas_fecha_null_analitica', filas_fecha_null,
  13, 'ventas_cero_o_negativas', ventas_no_positivas,
  14, 'descuentos_fuera_0_1', descuentos_fuera_rango,
  15, 'envios_anteriores_al_pedido', envios_anteriores,
  16, 'cantidades_no_positivas', cantidades_no_positivas,
  17, 'postales_cuatro_digitos', postales_cuatro_digitos,
  18, 'postales_con_cero_inicial', postales_cero_inicial,
  19, 'productos_con_espacios_ascii_extremos', productos_espacios_ascii,
  20, 'productos_con_espacio_no_separable', productos_espacio_no_separable
) s AS orden, indicador, valor
ORDER BY orden;
