# Pregunta 1 — diseño e implementación del modelo

## Enunciado y entregables

La primera pregunta del PDF exige construir el modelo de almacenamiento en
Hive, identificar los campos, elaborar un diccionario con tipos y restricciones,
crear una tabla analítica y documentar la carga con evidencia de registros
importados. Fuente: página 1 de `EXAMEN PRACTICO vF.pdf`.

## Estrategia

Se separan dos capas dentro de la base nueva `superstore_alexander_2mom`:

- `superstore_raw`: tabla externa con las 21 columnas como `STRING`, lectura
  mediante `OpenCSVSerde` y omisión de una sola cabecera. Conserva la entrada
  sin limpiar códigos postales, espacios ni caracteres especiales.
- `superstore`: tabla analítica con fechas, enteros y decimales explícitos,
  almacenada en ORC con SNAPPY. La granularidad es una línea de producto de una
  orden. `order_id` no es una clave única de línea.

La base y la ruta HDFS se comprobaron libres antes de crearlas. El ejecutor
rechaza una segunda ejecución si ya existe la base, la ruta o los registros de
salida; no utiliza eliminación ni sobrescritura para repetir la carga.

El [diccionario](diccionario_datos.md) detalla los 21 campos y sus expectativas
de calidad. Estas expectativas se comprobarán en la auditoría de la pregunta 2;
no se presentan como restricciones impuestas por el motor.

## Archivos y procedimiento ejecutado

1. [Preparación de la copia](../scripts/preparar_dataset.py): recodificación de
   Windows-1252 inferido a UTF-8 sin BOM. Cabecera y finales CRLF conservados.
2. [Ejecutor de carga](../scripts/cargar_superstore.py): comprobación de nombre
   y ruta libres, carga por entrada estándar de `hdfs dfs -put`, sin `-f`, y
   comparación del SHA-256 del archivo HDFS con la copia local.
3. [DDL](../scripts/01_modelo.sql): creación de la base, la tabla externa y la
   tabla analítica. La ruta externa es
   `hdfs://namenode:8020/user/dante/superstore_alexander_2mom/ingesta`.
4. [DML](../scripts/02_carga.sql): inserción en la tabla recién creada. Las
   fechas se interpretan con `M/d/yyyy`; zona UTC y formateador SIMPLE se fijan
   solo para la sesión. Se conservan cuatro decimales en ventas y ganancias.
5. [Comprobaciones HiveQL](../scripts/03_verificar_carga.sql): conteos, tipos y
   casos de prueba con comas, comillas literales y ceros iniciales.
6. Verificación independiente: el ejecutor recuperó los 21 campos de todas las
   filas desde Hive, ordenados por `row_id`, y los comparó en memoria con los
   valores esperados del CSV, interpretando fechas, enteros y decimales. No
   guardó ni versionó una segunda exportación completa del dataset.

El comando de ejecución inicial fue:

```powershell
wsl -d Ubuntu -- python3 -B scripts/cargar_superstore.py
```

**La carga ya se ejecutó. No repetir ese comando sobre el mismo entorno.** Para
consultar lo existente, sin volver a cargar:

```powershell
wsl -d Ubuntu -- python3 -B scripts/mostrar_carga.py
wsl -d Ubuntu -- python3 -B scripts/mostrar_carga.py --completo
```

## Resultados reales verificados

| Comprobación | Resultado |
|---|---:|
| Filas de `superstore_raw`, sin cabecera | 9.994 |
| Filas de `superstore` | 9.994 |
| Columnas comparadas por fila | 21 |
| Valores comparados con el CSV | 209.874 |
| Coincidencia tras aplicar los tipos previstos | Todos los valores |
| SHA-256 de la copia local y del archivo en HDFS | Coinciden |
| Hash del CSV original | Sin cambios |

Ejemplos obtenidos desde Hive:

- Fila 2: conserva la coma interna de `Hon Deluxe Fabric Upholstered Stacking
  Chairs, Rounded Back`; ventas `731.9400`, cantidad `3`, descuento `0.00` y
  ganancia `219.5820` permanecen en sus columnas.
- Fila 17: conserva las comillas de las dimensiones `72"H x 36"W x 18 1/2"D`.
- Filas 2235, 5275 y 8799: `postal_code` conserva el valor textual `05408`.
- Fila 1: `11/8/2016` se convirtió en `2016-11-08`, no en una fecha de agosto.

## Evidencia y estado

- [Registro de consola](../evidencias/p01_ejecucion.txt): comandos, salidas,
  advertencias y códigos de retorno reales. Es texto, no una captura.
- [Comprobaciones TSV](../evidencias/p01_comprobaciones.tsv): conteos, esquema
  y ejemplos reales.
- [Verificación JSON](../evidencias/p01_verificacion.json): resumen automático
  de la comparación completa y de los hashes.
- [Captura del estudiante](../evidencias/p01_modelo_carga.png): recibida y
  verificada visualmente; muestra ambas tablas con 9.994 filas. Se corrigió
  únicamente su nombre desde `evidenciasp01_modelo_carga.png`; el contenido y
  su SHA-256 se conservaron sin cambios.

La implementación, su comprobación y la captura están incorporadas.
La interpretación y la conclusión quedan disponibles para la revisión final
del estudiante antes de entregar.

## Interpretación técnica para revisar

Los conteos y la comparación completa muestran que la recodificación, el
lector CSV y la conversión de tipos preservaron las líneas y sus valores,
incluidos los campos que podrían desalinearse por comas internas. No se
descartaron filas ni se aplicaron correcciones silenciosas. Esto comprueba la
ingesta; no sustituye la auditoría de reglas de negocio de la pregunta 2.

El estudiante debe revisar esta interpretación y expresarla en sus propias
palabras antes de la entrega. La conclusión técnica provisional es que ambas
capas conservan los 9.994 registros y la semántica de los 21 campos.

## Advertencias encontradas

Beeline emitió advertencias por varias implementaciones SLF4J y por no poder
crear `/home/hive/.beeline`. Los comandos finalizaron con código 0 y las
comparaciones de datos fueron satisfactorias. No se modificó la configuración
del entorno existente para silenciar esas advertencias.

La prueba inicial del visualizador detectó que cortar el archivo por el primer
punto y coma seleccionaba solo parte de un comentario, sin ejecutar el conteo.
Se corrigió el recorte y se repitió la consulta: se observaron las dos filas
con 9.994 registros. No se dio por válida la primera prueba solo por su código
de retorno 0; el error no afectó a la carga ni a la comparación completa.
