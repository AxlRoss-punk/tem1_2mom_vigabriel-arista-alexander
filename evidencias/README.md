# Evidencias de ejecución

- `preparacion_ingesta.json`: registro automático real de la recodificación y
  de la comparación del CSV original con la copia. No es una captura.
- Los registros `.txt`, `.tsv` o `.json` deben proceder de comandos ejecutados.
- Las imágenes de cada pregunta serán capturas tomadas por el estudiante,
  con nombres como `p01_modelo_carga.png`.
- `p01_ejecucion.txt`, `p01_comprobaciones.tsv` y `p01_verificacion.json`
  corresponden a la carga real y a su verificación completa.
- `p01_modelo_carga.png`: captura del estudiante, recibida y verificada
  visualmente; muestra ambas tablas con 9.994 registros.
- `p02_resumen.tsv`, `p02_nulls.tsv`, `p02_incidencias.tsv`,
  `p02_ejecucion.txt` y `p02_verificacion.json`: auditoría real de la pregunta
  2, contrastada con el CSV original.
- `p02_ejecucion_intento1.txt`: registro del intento que Hive rechazó por un
  `ORDER BY` corregido posteriormente; no es el resultado válido de la auditoría.
- `p02_auditoria_calidad.png`: captura directa de la ventana de una ejecución
  real de Beeline, autorizada e inspeccionada visualmente.
- `p02_auditoria_calidad.captura.json`: procedencia de esa captura, con hashes,
  dimensiones, horas UTC y código de salida 0.
- No guardar tokens, contraseñas ni archivos de configuración privados.

- `07_*` a `18_*` y `21_*`: resultados TSV reales de las preguntas 3 a 8,
  sus registros TXT y procedencia `.ejecucion.json` con hashes y código 0.
- `analitica_verificacion.json`: comprobación final independiente de los
  resultados con el CSV. El informe inicial se conserva por separado.
- `p03_evolucion.png` y su `.captura.json`: captura real e inspeccionada de P3.
- `optimizacion_*`: mediciones de tiempos, tamaños y planes reales CSV/ORC.
- `intento_inicial_p07/`: intento descartado, claramente separado del resultado
  final correcto de 48 meses.
- Las capturas PNG de P4 a P8 están pendientes; los TSV y registros de esas
  preguntas sí proceden de ejecuciones verificadas.

La preparación no requiere capturas individuales. Las capturas se obtienen de
ejecuciones reales; las automatizadas se identifican mediante su registro de
procedencia. Los estados pendientes de los registros históricos corresponden
al momento de aquellas ejecuciones.
