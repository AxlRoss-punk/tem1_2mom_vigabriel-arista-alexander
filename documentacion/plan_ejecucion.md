# Metodología y alcance de la práctica

## Consigna de referencia

La práctica corresponde al documento `EXAMEN PRACTICO vF.pdf`, de seis páginas.
Su SHA-256 es
`843934a045fa56c3ab3d015c2761afdb329ae748987ea1bc6f42e56b37e48eee`.

El documento desarrolla ocho preguntas y solicita, en la sección de GitHub,
scripts para doce. Se trabajó con las ocho preguntas efectivamente enunciadas.
La diferencia de numeración queda pendiente de aclaración con el docente.

## Desarrollo del trabajo

| Etapa | Procedimiento | Comprobación |
|---|---|---|
| Inspección | Revisar bytes, cabecera, fechas, números y reglas CSV | 9.994 filas, 21 columnas y características documentadas |
| Preparación | Recodificar una copia a UTF-8 sin BOM | Hash del original intacto e igualdad de todos los campos |
| Modelado | Separar ingesta textual de tabla analítica ORC | Tipos explícitos y conservación de 209.874 valores |
| Auditoría | Revisar duplicados, NULL, fechas, ventas y descuentos | Consultas Hive y contraste independiente con el CSV |
| Análisis | Aplicar agregaciones, CTE y ventanas | Resultados de las preguntas 3 a 8 contrastados |
| Optimización | Comparar consultas equivalentes sobre CSV y ORC | Tiempos, tamaños HDFS, planes e igualdad de resultados |
| Documentación | Relacionar consultas, resultados, interpretación y evidencia | Archivos identificados por pregunta y commits progresivos |

## Decisiones de modelado y análisis

La unidad de observación es una línea de producto de una orden. Por ello,
`order_id` puede repetirse y la auditoría de duplicados se realiza sobre
`row_id`. Las fechas se interpretan como mes/día/año; los códigos postales
se conservan como texto y las pérdidas como valores negativos.

Se distingue entre ganancia absoluta y margen, y entre ventas monetarias y
unidades. Los criterios de desempate, las puntuaciones RFM y el tratamiento
de ganancias negativas en Pareto se explican junto a cada consulta.

Las reglas de calidad se auditan, no se presentan como restricciones impuestas
automáticamente por Hive. No se aplicaron correcciones silenciosas a códigos
postales, espacios ni valores originales.

## Conservación y aislamiento

El CSV y el PDF originales se utilizaron en modo lectura. La base
`superstore_alexander_2mom` y su ruta de ingesta son independientes de
`db_alexander`, `dbec_alexander`, `db3_alexander` y `db4_alexander`.
No se modificaron esas bases ni se eliminaron contenedores o volúmenes.

La copia local y los archivos temporales se excluyen de Git. Las salidas se
guardan sin sobrescribir registros anteriores; los intentos descartados se
identifican por separado.

## Verificación y evidencias

Cada ejecución registrada incluye su comando, código de salida y salida real.
Los informes analíticos añaden hashes del SQL y del resultado. La verificación
independiente vuelve a calcular las métricas a partir del CSV original.

Las capturas disponibles corresponden a ventanas de ejecuciones reales.
La primera se tomó manualmente; las siguientes se obtuvieron mediante captura
directa de la ventana de terminal y conservan metadatos de procedencia.
Los TXT, TSV y JSON se identifican como registros, no como capturas de pantalla.

Las preguntas 1 a 3 tienen capturas incorporadas. Las preguntas 4 a 8 cuentan
con resultados y registros; sus capturas PNG siguen pendientes.

## Declaración de uso de herramientas

Se utilizaron herramientas de inteligencia artificial como apoyo en la
preparación de código y verificaciones, bajo la autorización docente indicada
para esta práctica. La responsabilidad sobre la revisión, comprensión e
interpretación del contenido corresponde al estudiante.
