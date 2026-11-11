# Conclusiones

1. La separación entre ingesta textual y tabla analítica permitió conservar
   los 9.994 registros y sus 21 campos, con comas internas, comillas y códigos
   postales. El CSV original conserva su hash.
2. La auditoría no detectó incumplimientos en las reglas requeridas, aunque
   permanecen observaciones de formato postal y espacios documentadas.
3. West alcanza la mayor ganancia acumulada; Central presenta menor ganancia
   y margen pese a superar la facturación de South. La rentabilidad requiere
   examinar ambas magnitudes.
4. RFM distingue 104 clientes de alto valor y 201 en riesgo bajo los criterios
   relativos elegidos. Son segmentos descriptivos que requieren validación
   comercial antes de utilizarlos como decisiones operativas.
5. El ranking por ventas, unidades, margen y ganancia ofrece perspectivas
   diferentes. La mayor pérdida absoluta y el peor margen pertenecen a
   productos distintos.
6. Las 856 líneas con descuentos superiores a 50% presentan pérdidas. Existe
   asociación en el dataset; la comparación no demuestra causalidad.
7. La serie contiene 48 meses. Las comparaciones y medias móviles respetan
   la ausencia de antecedentes y no sustituyen esos valores por ceros.
8. El 80% de ventas se alcanza con 414 productos; el 80% de ganancia neta,
   con 164. Los productos de pérdida deben conservarse y su efecto sobre el
   acumulado de ganancia debe explicarse.
9. ORC redujo el tamaño lógico medido y tuvo menor mediana de tiempo en esta
   prueba pequeña. Las limitaciones de caché, cliente y pocas repeticiones
   impiden generalizar el rendimiento.

Las consultas y los resultados están ejecutados y contrastados. La trazabilidad
se mantiene mediante scripts, registros y hashes. Quedan pendientes las capturas
PNG de las preguntas 4 a 8 como parte de la presentación de evidencias.
