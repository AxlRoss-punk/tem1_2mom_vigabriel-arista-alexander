# Índice de evidencias

Esta carpeta conserva las salidas obtenidas durante la ejecución de la
práctica. Los archivos se distinguen por su función:

| Formato | Contenido |
|---|---|
| TSV | Resultados tabulares devueltos por Hive |
| TXT | Comandos, salidas, advertencias y códigos de retorno |
| JSON | Verificaciones, hashes, tiempos y procedencia |
| PNG | Capturas de ventanas de ejecución |

## Preparación y preguntas 1–2

- `preparacion_ingesta.json`: integridad de la recodificación del CSV.
- `p01_*`: conteos, esquema, ejemplos, comparación de campos y captura de carga.
- `p02_*`: auditoría, NULL por columna, incidencias y revalidación.
- `p02_ejecucion_intento1.txt`: intento rechazado por Hive, conservado como
  antecedente del error de ordenación corregido.
- `p02_auditoria_calidad.captura.json`: procedencia de la captura de auditoría.

## Preguntas 3–8 y optimización

- `07_*` a `18_*` y `21_*`: resultados analíticos, registros y archivos
  `.ejecucion.json` con hashes y código de salida.
- `analitica_verificacion.json`: comprobación final independiente; el informe
  inicial se conserva en un archivo separado.
- `p03_evolucion.png` y su `.captura.json`: captura de la evolución regional.
- `optimizacion_*`: tiempos, tamaños y planes de las consultas CSV/ORC.
- `intento_inicial_p07/`: resultado descartado, separado de la serie mensual
  final correcta de 48 meses.

## Alcance de las capturas

Las imágenes disponibles corresponden a las preguntas 1, 2 y 3. La primera
fue tomada manualmente; las de P2 y P3 se capturaron directamente de ventanas
de terminal tras ejecutar las consultas. Los metadatos permiten identificar
el SQL y comprobar la integridad de cada imagen.

Las capturas de P4 a P8 están pendientes. Sus TSV y registros están incluidos.
Los archivos de texto y las comprobaciones JSON no se presentan como imágenes.
