# Resumen de resultados y entregables

**Práctica:** Apache Hive — Sample Superstore

**Estudiante:** Alexander Vigabriel

**Fecha de referencia:** 11 de noviembre de 2026

## Estado por pregunta

| Pregunta | Trabajo realizado | Evidencia disponible |
|---|---|---|
| 1. Modelo y carga | Diccionario, DDL, carga y comparación de 209.874 valores | Registros, verificación JSON y captura |
| 2. Auditoría | Controles del PDF y contraste con el CSV | TSV, registros, verificación JSON y captura |
| 3. Evolución regional | Ventas, ganancias, márgenes y variaciones anuales | TSV, registros, verificación y captura |
| 4. RFM | Medidas, puntuaciones y segmentos de 793 clientes | TSV y registros; captura PNG pendiente |
| 5. Productos | Ranking de 1.862 productos por ganancia, margen, ventas y unidades | TSV y registros; captura PNG pendiente |
| 6. Descuentos | Cuatro rangos y detalle por categoría/subcategoría | TSV y registros; captura PNG pendiente |
| 7. Tendencias | Serie de 48 meses, variaciones, medias móviles y extremos | TSV y registros; captura PNG pendiente |
| 8. Pareto | Participaciones y cortes del 80% de ventas y ganancia neta | TSV y registros; captura PNG pendiente |

Las consultas de las ocho preguntas están ejecutadas. El informe
`analitica_verificacion.json` recoge 61.428 comprobaciones satisfactorias de
las preguntas 3 a 8. La optimización medida y las conclusiones también están
documentadas.

## Resultados de control

- 9.994 registros, 5.009 órdenes únicas y 793 clientes.
- Cero identificadores de fila duplicados y cero NULL en las 21 columnas.
- Cero incumplimientos en los controles de fechas, ventas y descuentos requeridos.
- 438 códigos postales de cuatro dígitos, conservados como texto.
- 16 nombres con espacios exteriores y 225 con espacios no separables.

El CSV original conserva el SHA-256
`58fb59c63089e564d835e4aabe19d371757de1137a5bf1888243ae386c4b7a97`.
Las bases de las prácticas anteriores permanecen intactas.

## Evidencias y trazabilidad

Las capturas de las preguntas 1 a 3 muestran resultados reales de Beeline.
Las capturas automatizadas conservan sus hashes, dimensiones, horas UTC y
código de salida en archivos `.captura.json`.

Los registros originales y los intentos descartados se conservan por separado.
El intento inicial de P7 se identificó como incorrecto y se sustituyó, en los
resultados finales, por una serie de 48 meses contrastada con el CSV. Los
campos de estado de registros históricos describen el momento de su ejecución.

## Pendientes

Faltan las capturas PNG de las preguntas 4 a 8 y la revisión final de
presentación. Sus resultados tabulares y registros de ejecución están
disponibles. La diferencia entre las ocho preguntas enunciadas y los doce
scripts mencionados en la consigna queda señalada para aclaración.
