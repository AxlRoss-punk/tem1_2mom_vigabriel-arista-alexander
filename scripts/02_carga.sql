-- Pregunta 1. Solo se inserta en la tabla nueva y vacía creada por 01_modelo.sql.
-- Opciones de sesión; no cambian la configuración global del servidor.
SET hive.local.time.zone=UTC;
SET hive.datetime.formatter=SIMPLE;

INSERT INTO TABLE superstore_alexander_2mom.superstore
SELECT
  CAST(row_id AS INT),
  order_id,
  TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(order_date, 'M/d/yyyy'))),
  TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(ship_date, 'M/d/yyyy'))),
  ship_mode,
  customer_id,
  customer_name,
  segment,
  country,
  city,
  state,
  postal_code,
  region,
  product_id,
  category,
  sub_category,
  product_name,
  CAST(sales AS DECIMAL(12,4)),
  CAST(quantity AS INT),
  CAST(discount AS DECIMAL(3,2)),
  CAST(profit AS DECIMAL(12,4))
FROM superstore_alexander_2mom.superstore_raw;
