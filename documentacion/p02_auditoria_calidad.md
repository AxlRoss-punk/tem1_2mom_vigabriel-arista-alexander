# Pregunta 2 — auditoría de calidad e integridad

## Enunciado

La pregunta 2 del PDF solicita determinar registros totales, identificadores
de fila duplicados, órdenes y clientes únicos, campos con NULL, fechas
inválidas o inconsistentes, ventas no positivas, descuentos fuera del intervalo
esperado y envíos anteriores al pedido. Exige una consulta de resumen y
criterios de tratamiento de las inconsistencias. Fuente: páginas 1 y 2 de
`EXAMEN PRACTICO vF.pdf`.

## Cobertura de los requisitos del PDF

| Requisito de la pregunta 2 | Comprobación ejecutada | Resultado |
|---|---|---|
| Cantidad total de registros | Conteos independientes de origen y tabla analítica en `04_p02_resumen.sql` | 9.994 en ambas capas |
| Identificadores de fila duplicados | Agrupación por `row_id`, grupos repetidos y filas adicionales | 0 grupos; 0 filas adicionales |
| Órdenes y clientes únicos | `COUNT(DISTINCT order_id)` y `COUNT(DISTINCT customer_id)` | 5.009 órdenes; 793 clientes |
| Campos con NULL | Conteos por las 21 columnas en `05_p02_nulls.sql` y total en el resumen | 0 en cada columna |
| Fechas inválidas o inconsistentes | Reconversión de fechas originales, fechas nulas finales y comparación pedido/envío | 0 incidencias |
| Ventas iguales o inferiores a cero | Condición `sales <= 0` | 0 registros |
| Descuentos fuera del intervalo esperado | Condición `discount < 0 OR discount > 1` | 0 registros |
| Envío anterior al pedido | Condición `ship_date < order_date` | 0 registros |
| Consulta de resumen de calidad | `04_p02_resumen.sql`, ejecutado mediante Beeline | 20 indicadores reales |
| Criterios de tratamiento | Tabla de criterios incluida en este documento | Propuestas documentadas; sin alterar datos |

## Estrategia y reglas

La auditoría utiliza únicamente consultas sobre `superstore_alexander_2mom`.
No modifica filas, tablas ni bases anteriores.

1. Contar registros de la tabla analítica y del origen textual por separado.
2. Agrupar por `row_id` no nulo y detectar grupos con más de una fila.
   Se distinguen los identificadores repetidos de las filas adicionales:
   un identificador con tres apariciones cuenta como un grupo y dos filas
   adicionales. Los identificadores nulos se contabilizan como NULL.
3. Contar órdenes y clientes distintos. Una orden puede contener varias
   líneas, por lo que repetir `order_id` no constituye un duplicado de fila.
4. Contar NULL en las 21 columnas, tanto por campo como por fila. El total de
   valores NULL es `21 * COUNT(*)` menos la suma de los conteos no nulos.
   El literal textual `NULL` y una cadena vacía no se equiparan automáticamente
   a un NULL del motor; los indicadores publicados aquí miden NULL reales.
5. Comprobar fechas también en `superstore_raw`. Después de interpretar
   `M/d/yyyy`, se reconvierte al mismo formato y se compara con el texto sin
   espacios exteriores. Esto detecta fechas normalizadas por un lector
   permisivo, como un día inexistente que se traslada al mes siguiente.
   Además se comprueban fechas nulas en la tabla final y `ship_date < order_date`.
6. Considerar inconsistentes las ventas menores o iguales a cero, los
   descuentos fuera de `[0,1]` y, como control adicional, cantidades no
   positivas. El descuento se interpreta como fracción: `0.20` equivale a 20%.
7. Separar las observaciones de formato postal y espacios de los
   incumplimientos de reglas numéricas y cronológicas.

## HiveQL y ejecución

- [Resumen de calidad](../scripts/04_p02_resumen.sql): CTE con agregaciones,
  duplicados y validación del origen; `STACK` presenta los indicadores como
  filas ordenadas.
- [NULL por columna](../scripts/05_p02_nulls.sql): las 21 columnas, incluidas
  aquellas con cero NULL.
- [Detalle de incidencias](../scripts/06_p02_incidencias.sql): filas con
  incumplimientos numéricos o cronológicos y una muestra de códigos postales
  de cuatro dígitos.
- [Ejecutor y contraste](../scripts/auditar_calidad.py): ejecuta los archivos
  mediante Beeline, registra las salidas reales y contrasta todos los
  indicadores y conteos NULL con una lectura independiente del CSV original.

Comando ejecutado desde la raíz del repositorio:

```powershell
wsl -d Ubuntu -- python3 -B scripts/auditar_calidad.py
```

La ejecución ya generó los registros. El comando rechaza sobrescribirlos.
Para volver a consultar el resumen sin escribir archivos:

```powershell
wsl -d Ubuntu -- python3 -B scripts/auditar_calidad.py --mostrar
```

`SET` fija únicamente la zona horaria UTC y el formateador SIMPLE de la sesión.
El resto de las instrucciones son de lectura. No se ejecutó DDL ni DML.

## Resultados reales

| Indicador | Resultado |
|---|---:|
| Registros analíticos | 9.994 |
| Registros del origen textual, sin cabecera | 9.994 |
| Identificadores de fila repetidos | 0 |
| Filas duplicadas adicionales | 0 |
| Órdenes únicas | 5.009 |
| Clientes únicos | 793 |
| Filas con algún NULL | 0 |
| Valores NULL sumados en las 21 columnas | 0 |
| Fechas de pedido inválidas en el origen | 0 |
| Fechas de envío inválidas en el origen | 0 |
| Filas con alguna fecha inválida en el origen | 0 |
| Filas con fecha nula en la tabla analítica | 0 |
| Ventas iguales o inferiores a cero | 0 |
| Descuentos fuera de [0,1] | 0 |
| Envíos anteriores al pedido | 0 |
| Cantidades no positivas | 0 |

Las 21 columnas devolvieron individualmente cero NULL. La consulta de
incidencias numéricas y cronológicas no devolvió filas. Las métricas de Hive
y los conteos por columna coincidieron con la comprobación independiente del
CSV original. Su SHA-256 permanece sin cambios:
`58fb59c63089e564d835e4aabe19d371757de1137a5bf1888243ae386c4b7a97`.

Observaciones adicionales verificadas en Hive:

| Observación | Registros afectados |
|---|---:|
| Código postal de cuatro dígitos | 438 |
| Código postal con cero inicial conservado | 11 |
| Nombre de producto con espacios ASCII en los extremos | 16 |
| Nombre de producto con algún espacio no separable U+00A0 | 225 |

Ejemplos postales: fila 186, `6824`, Fairfield; fila 198, `7090`, Westfield;
fila 268, `7960`, Morristown. La longitud de cuatro dígitos sugiere ceros
iniciales perdidos previamente, pero la auditoría no confirma ni corrige esa
suposición mediante una fuente postal externa.

## Criterios de tratamiento

| Situación | Criterio propuesto |
|---|---|
| `row_id` repetido | Revisar las filas completas y su procedencia antes de decidir si se trata de un duplicado; no deduplicar por `order_id` |
| NULL en campos necesarios | Conservar el registro de origen e identificar la causa; corregir solo con una regla y fuente justificadas |
| Fecha inválida o envío anterior al pedido | Separar para revisión; no inventar fechas ni intercambiar pedido y envío automáticamente |
| Venta no positiva o descuento fuera de [0,1] | Revisar la operación y documentar el criterio de inclusión en análisis posteriores |
| Cantidad no positiva | Revisar si corresponde a un error o a una operación especial antes de excluirla |
| Código postal de cuatro dígitos | Mantener `STRING` y el valor original; validar cualquier relleno de ceros antes de aplicarlo |
| Espacios exteriores o U+00A0 | Conservar el origen; si afectan agrupaciones, normalizar solo en una capa derivada y registrar los cambios |
| Beneficio negativo | Conservarlo como pérdida comercial; el signo por sí solo no constituye un error de integridad |

Estos criterios son propuestas; no se aplicó limpieza, imputación ni
eliminación de registros. En los controles requeridos no se encontraron
incumplimientos que exigieran intervenir sobre los datos.

## Interpretación y conclusión

Las 9.994 líneas corresponden a 5.009 órdenes y 793 clientes. La diferencia
entre líneas y órdenes es coherente con el nivel de detalle del modelo.
Los controles comprobados no detectan duplicación de identificadores,
ausencias tipadas ni incumplimientos numéricos y cronológicos. Las observaciones
postales y de espacios deben conservarse documentadas al diseñar los análisis.

La implementación, la ejecución y la evidencia visual están incorporadas.
Las observaciones de formato se mantienen en el informe sin alterar los
registros, de modo que cualquier limpieza posterior pueda justificarse.

## Evidencias y errores registrados

- [Resumen real](../evidencias/p02_resumen.tsv).
- [NULL por columna](../evidencias/p02_nulls.tsv).
- [Detalle y muestra postal](../evidencias/p02_incidencias.tsv).
- [Consola de la ejecución correcta](../evidencias/p02_ejecucion.txt).
- [Verificación independiente](../evidencias/p02_verificacion.json).
- [Primer intento rechazado](../evidencias/p02_ejecucion_intento1.txt): Hive
  rechazó `ORDER BY orden` porque la columna no estaba proyectada. Se añadió
  `orden` al resultado del resumen y del desglose NULL; después se ejecutaron
  correctamente las tres consultas. El intento fallido no modificó datos.
- Persisten las advertencias de SLF4J y `/home/hive/.beeline` ya documentadas;
  la ejecución correcta terminó con código 0.
- [Captura real de la auditoría](../evidencias/p02_auditoria_calidad.png):
  obtenida automáticamente de una ventana exclusiva de Windows Terminal,
  después de ejecutar el SQL con código de salida 0; inspeccionada visualmente.
- [Procedencia de la captura](../evidencias/p02_auditoria_calidad.captura.json):
  hashes del SQL y del PNG, dimensiones, horas UTC y código de salida.

La captura de carga está en `evidencias/p01_modelo_carga.png`. La captura de
auditoría se obtuvo de una ventana de ejecución real y conserva sus píxeles
sin edición; los metadatos identifican la consulta y el archivo de imagen.

## Verificación de reproducibilidad

El 11 de noviembre de 2026 se comprobó que
`evidencias/p01_modelo_carga.png` existe y conserva el SHA-256 de la captura
ya inspeccionada. También se comprobó que el PDF original conserva el hash de
la versión revisada.

Se volvieron a ejecutar en Hive los tres scripts de auditoría. Todas las
consultas terminaron con código 0; las salidas coincidieron byte por byte con
los TSV anteriores. Los 20 indicadores y los conteos NULL de las 21 columnas
volvieron a coincidir con la lectura independiente del CSV original. No se
modificaron tablas ni se sobrescribieron los registros de la primera auditoría.

- [Registro de la revalidación](../evidencias/p02_revalidacion.txt).
- [Resultado y comparaciones](../evidencias/p02_revalidacion.json).

La captura `evidencias/p02_auditoria_calidad.png` ya está incorporada. Los
registros históricos que indicaban su ausencia se conservan como constancia
del estado en el momento de cada ejecución.
