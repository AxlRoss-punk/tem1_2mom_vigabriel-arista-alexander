# Optimización: medición real de CSV y ORC

Se comparó la misma agregación de ventas y ganancias por región y año sobre
CSV textual y sobre la tabla analítica ORC con SNAPPY. Ambos formatos
devolvieron las mismas 16 filas y valores.

| Formato | Tamaño lógico HDFS, bytes | Mediana medida, segundos |
|---|---:|---:|
| CSV UTF-8 | 2288516 | 6.641829 |
| ORC SNAPPY | 354612 | 5.735196 |

La reducción del tamaño lógico fue **84.5047%**. En esta medición ORC tuvo
menor tiempo de pared. El tiempo incluye Docker, arranque de Beeline,
conexión y consulta; no representa exclusivamente el motor Hive.

El procedimiento ejecutó un calentamiento por formato y dos repeticiones
medidas por formato, alternando el orden. No se vaciaron cachés ni se
modificaron configuraciones globales. El dataset es pequeño; caché y arranque
del cliente influyen, por lo que no se afirma una ventaja universal ni una
estimación estadística de rendimiento.

- Consultas: [CSV](../scripts/19_optimizar_csv.sql) y
  [ORC](../scripts/20_optimizar_orc.sql).
- Ejecutor: [medir_optimizacion.py](../scripts/medir_optimizacion.py).
- [Mediciones completas](../evidencias/optimizacion_mediciones.json) y
  [consola real](../evidencias/optimizacion_ejecucion.txt).
- Planes obtenidos mediante EXPLAIN: [CSV](../evidencias/optimizacion_plan_csv.txt)
  y [ORC](../evidencias/optimizacion_plan_orc.txt).

La tabla tipada evita repetir conversiones del CSV; las consultas agregan antes
de las ventanas y seleccionan las medidas necesarias. No se añadieron
particiones a solo 9.994 filas. Particionamiento y estadísticas adicionales son
posibles pruebas futuras si aumenta la escala, no optimizaciones ejecutadas en
esta entrega. Los tamaños son lógicos, sin multiplicar por replicación HDFS.
