# Diccionario de datos — pregunta 1

Una fila representa una línea de producto de una orden. Una orden puede
contener varias filas; por tanto, `order_id` no debe tratarse como clave única
de esta tabla. Se conserva el orden de las 21 columnas del CSV.

Todas las columnas de `superstore_raw` son `STRING`, para preservar la entrada
y evitar conversiones implícitas. Los tipos siguientes corresponden a la tabla
analítica `superstore`. Las reglas son expectativas que deben auditarse; no
se presentan como restricciones que Hive esté imponiendo automáticamente.

| N.º | Campo original | Columna Hive | Tipo analítico | Descripción y regla de calidad |
|---:|---|---|---|---|
| 1 | Row ID | row_id | INT | Identificador de línea; se espera no nulo y único |
| 2 | Order ID | order_id | STRING | Identificador de orden; puede repetirse entre líneas |
| 3 | Order Date | order_date | DATE | Fecha del pedido; origen M/d/yyyy |
| 4 | Ship Date | ship_date | DATE | Fecha de envío; se espera que no anteceda al pedido |
| 5 | Ship Mode | ship_mode | STRING | Modalidad de envío registrada |
| 6 | Customer ID | customer_id | STRING | Identificador del cliente; puede repetirse |
| 7 | Customer Name | customer_name | STRING | Nombre registrado; conservar caracteres especiales |
| 8 | Segment | segment | STRING | Segmento comercial del cliente |
| 9 | Country | country | STRING | País de la operación |
| 10 | City | city | STRING | Ciudad de la operación |
| 11 | State | state | STRING | Estado de la operación |
| 12 | Postal Code | postal_code | STRING | Código postal; conservar ceros y longitud originales |
| 13 | Region | region | STRING | Región comercial |
| 14 | Product ID | product_id | STRING | Identificador del producto; puede repetirse |
| 15 | Category | category | STRING | Categoría de producto |
| 16 | Sub-Category | sub_category | STRING | Subcategoría de producto |
| 17 | Product Name | product_name | STRING | Nombre; admite comas y comillas literales |
| 18 | Sales | sales | DECIMAL(12,4) | Importe de venta; auditar valores menores o iguales a cero |
| 19 | Quantity | quantity | INT | Unidades de la línea; se esperan enteros positivos |
| 20 | Discount | discount | DECIMAL(3,2) | Fracción de descuento; intervalo esperado [0,1] |
| 21 | Profit | profit | DECIMAL(12,4) | Ganancia de la línea; los negativos representan pérdidas válidas |

La precisión de ventas y ganancias permite ocho dígitos enteros y cuatro
decimales, con margen sobre los valores observados. No se redondean a dos
decimales los valores originales de cuatro posiciones. Descuento `0.20`
representa 20%; no es el número 20.

No se completan códigos postales de cuatro dígitos ni se recortan espacios
sin una regla de limpieza validada. Se conserva el texto de la entrada.

La tabla analítica utiliza ORC con compresión SNAPPY. Es una decisión inicial
de almacenamiento, no una afirmación de mejora de rendimiento medida. No se
particionan las 9.994 filas de esta práctica sin justificar el beneficio.

Referencia: [CSV SerDe de Apache Hive](https://hive.apache.org/docs/latest/user/csv-serde/).
