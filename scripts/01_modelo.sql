-- Pregunta 1. Ejecutar solo con un nombre de base libre.
CREATE DATABASE superstore_alexander_2mom
COMMENT 'Examen individual Superstore; espacio independiente';

CREATE EXTERNAL TABLE superstore_alexander_2mom.superstore_raw (
  row_id STRING,
  order_id STRING,
  order_date STRING,
  ship_date STRING,
  ship_mode STRING,
  customer_id STRING,
  customer_name STRING,
  segment STRING,
  country STRING,
  city STRING,
  state STRING,
  postal_code STRING,
  region STRING,
  product_id STRING,
  category STRING,
  sub_category STRING,
  product_name STRING,
  sales STRING,
  quantity STRING,
  discount STRING,
  profit STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ('separatorChar'=',', 'quoteChar'='"')
STORED AS TEXTFILE
LOCATION 'hdfs://namenode:8020/user/dante/superstore_alexander_2mom/ingesta'
TBLPROPERTIES ('skip.header.line.count'='1');

CREATE TABLE superstore_alexander_2mom.superstore (
  row_id INT,
  order_id STRING,
  order_date DATE,
  ship_date DATE,
  ship_mode STRING,
  customer_id STRING,
  customer_name STRING,
  segment STRING,
  country STRING,
  city STRING,
  state STRING,
  postal_code STRING,
  region STRING,
  product_id STRING,
  category STRING,
  sub_category STRING,
  product_name STRING,
  sales DECIMAL(12,4),
  quantity INT,
  discount DECIMAL(3,2),
  profit DECIMAL(12,4)
)
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY');
