# Estado de entrega — 11 de noviembre de 2026

Se prioriza publicar el trabajo ejecutado, comprobado y documentado. Se detuvo
el desarrollo de automatizaciones adicionales ante la proximidad de la entrega.

| Pregunta | Estado técnico | Evidencia |
|---|---|---|
| 1. Modelo y carga | Implementada y verificada: 9.994 filas en ambas tablas; 209.874 valores comparados | `evidencias/p01_modelo_carga.png`, registros y verificación JSON |
| 2. Auditoría de calidad | Ejecutada y contrastada con el CSV; cobertura de todos los requisitos documentada | `evidencias/p02_auditoria_calidad.png`, TSV, registros y verificaciones JSON |
| 3. Evolución comercial por región | Ejecutada y contrastada; documentada | TSV, registros, hashes y captura PNG real |
| 4. Segmentación RFM | Ejecutada y contrastada: 793 clientes | TSV y registros reales; falta captura PNG |
| 5. Ranking de productos | Ejecutada y contrastada: 1.862 productos; importe y unidades | TSV y registros reales; falta captura PNG |
| 6. Impacto de descuentos | Ejecutada y contrastada: cuatro rangos y detalle por subcategoría | TSV y registros reales; falta captura PNG |
| 7. Tendencias temporales | Ejecutada y contrastada: 48 meses y extremos | TSV y registros reales; falta captura PNG |
| 8. Pareto de ventas y ganancias | Ejecutada y contrastada: cortes 414 y 164 productos | TSV y registros reales; falta captura PNG |

El análisis medido de optimización y las conclusiones técnicas están
documentados. Quedan pendientes las cinco capturas indicadas y la revisión
final de las interpretaciones por el estudiante. El informe
`evidencias/analitica_verificacion.json` registra 61.428 comprobaciones
independientes satisfactorias de las preguntas 3 a 8.

Los resultados e interpretaciones de esas seis preguntas están en
`p03_p08_resultados.md`. La medición en `optimizacion.md` registra 2.288.516
bytes de CSV frente a 354.612 de ORC, con igualdad de resultados y límites
explícitos de la prueba. Las conclusiones están en `conclusiones.md`.

## Resultados comprobados de la auditoría

- 9.994 registros, 5.009 órdenes únicas y 793 clientes.
- Cero identificadores de fila duplicados y cero NULL en las 21 columnas.
- Cero fechas inválidas, envíos anteriores al pedido, ventas no positivas o
  descuentos fuera de `[0,1]`, bajo las reglas documentadas.
- Se conservan observaciones: 438 códigos postales de cuatro dígitos, 16
  nombres con espacios exteriores y 225 con espacios no separables.
- Las tres consultas se revalidaron y coincidieron con los registros anteriores
  y con una comprobación independiente del CSV original.

## Capturas reales y conservación

La captura de la pregunta 1 fue proporcionada por el estudiante e inspeccionada.
La de la pregunta 2 se obtuvo, con su autorización, capturando directamente los
píxeles de una ventana exclusiva de Windows Terminal después de ejecutar
`04_p02_resumen.sql` en Beeline con código de salida 0. La imagen se inspeccionó
visualmente y conserva sus píxeles sin edición.

La procedencia de la segunda captura está en
`evidencias/p02_auditoria_calidad.captura.json`: hash del SQL, hash del PNG,
horas UTC, dimensiones y código de salida. Los campos de capturas pendientes
en registros históricos describen el momento de aquellas ejecuciones; el
estado actual es el de este documento y las imágenes incorporadas.

La captura de la pregunta 3 también se obtuvo de una ejecución real y se
inspeccionó visualmente. Se conserva su registro `.captura.json`. La captura de
P4 se detuvo al no poder garantizar que la ventana correcta estuviera delante;
no se guardó una imagen ni se prosiguió con P5–P8 tras la instrucción urgente.

El CSV original conserva el SHA-256
`58fb59c63089e564d835e4aabe19d371757de1137a5bf1888243ae386c4b7a97`.
No se modificaron las bases `db_alexander`, `dbec_alexander`, `db3_alexander`
ni `db4_alexander`. La copia del dataset y los archivos temporales permanecen
fuera del versionado mediante `.gitignore`.

Los errores y advertencias ya encontrados permanecen documentados en los
registros de ejecución; se conserva también el intento inicial fallido de la
auditoría. El intento inicial incorrecto de P7 está separado y marcado como
descartado; los resultados finales contienen 48 meses y están verificados.
No se inventaron resultados ni capturas faltantes.
