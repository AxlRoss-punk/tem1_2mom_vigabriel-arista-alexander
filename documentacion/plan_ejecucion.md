# Plan de ejecución y condiciones académicas

## Consigna revisada

- Archivo original leído: `C:\Users\dante\Downloads\EXAMEN PRACTICO vF.pdf`.
- Extensión: seis páginas; tamaño: 329.706 bytes.
- SHA-256: `843934a045fa56c3ab3d015c2761afdb329ae748987ea1bc6f42e56b37e48eee`.
- Se leyó mediante pypdf 7.0.1 en una carpeta temporal, sin instalar paquetes
  globales ni modificar el PDF.
- El 11 de noviembre de 2026 el estudiante confirmó en el chat que el docente
  autorizó desarrollar las soluciones con IA. Esta es una confirmación del
  estudiante; no se presenta como una autorización documental del docente.
- Se declara el uso de IA como apoyo para preparación, código y verificación.
  El estudiante debe comprender el código y redactar su interpretación en sus
  propias palabras, como exige el PDF.

## Discrepancia pendiente de consulta al docente

Las páginas 1 a 4 desarrollan **ocho preguntas**. La sección 4, página 4,
solicita scripts para **doce preguntas**. Se trabajará con las ocho preguntas
efectivamente enunciadas; no se inventarán preguntas 9 a 12. El estudiante debe
consultar esta discrepancia al docente.

## Bloques y criterios de cierre

| Hito | Alcance | Verificación y evidencia |
|---|---|---|
| Preparación | Revisar consigna y documentación; recodificar una copia; declarar uso de IA | Hash original intacto, UTF-8 válido, igualdad de 9.994 filas y 21 campos; registro JSON |
| I, pregunta 1 | Diccionario, base independiente, ingesta textual y tabla analítica, DDL y carga | Ejecución real, tipos, conteos y casos con comillas; captura del estudiante |
| I, pregunta 2 | Auditoría: filas, duplicados, órdenes y clientes únicos, NULL, fechas, ventas y descuentos | Resumen ejecutado en Hive, criterios de tratamiento y captura |
| II, pregunta 3 | Ventas, ganancias, margen y variación anual por región; extremos de desempeño | CTE y ventanas ejecutadas; definición del indicador de desempeño y captura |
| II, pregunta 4 | RFM con fecha máxima del dataset, órdenes únicas y ventas por cliente | Justificación de puntuaciones y segmentos; resultados y captura |
| II, pregunta 5 | Rankings de productos, ventas, ganancias y márgenes | RANK, DENSE_RANK y acumulados; criterios de empate y captura |
| II, pregunta 6 | Rangos de descuento definidos por el PDF; pérdidas y rentabilidad | Rangos 0, (0;0,20], (0,20;0,50], >0,50; resultados y captura |
| III, pregunta 7 | Evolución mensual, comparación interanual y promedio móvil de tres meses | Calendario mensual completo y ventanas comprobadas; captura |
| III, pregunta 8 | Pareto independiente de ventas y ganancias por producto | Tratamiento explícito de ganancias negativas y del cruce del 80%; captura |
| Cierre | Optimización, conclusiones y procedimiento reproducible | Evidencias auténticas, revisión del repositorio y commits progresivos |

Cada pregunta debe incluir enunciado, estrategia, HiveQL, evidencia, resultado
real, interpretación del estudiante y conclusión específica. Un archivo SQL
sin ejecutar no constituye una pregunta terminada.

## Aislamiento y seguridad

- Original CSV y PDF: solo lectura.
- Bases protegidas: `db_alexander`, `dbec_alexander`, `db3_alexander`,
  `db4_alexander`; no se reutilizarán ni modificarán.
- Nombre propuesto: `superstore_alexander_2mom`. La consulta inicial en Hive no
  devolvió una base con ese nombre. La creación debe fallar si ya existe;
  no se utilizará `IF NOT EXISTS` para ocultar una colisión.
- Se usarán rutas propias para los datos de esta práctica y no se sobrescribirán
  archivos existentes. La copia local en `datos/` queda excluida de Git.
- No se ejecutarán eliminaciones masivas, `down -v` ni `volume prune`.
- El estudiante autorizó usar la credencial existente de `AxlRoss-punk` para
  publicar y verificar los hitos. No se autorizan cambios globales ni nuevas
  modificaciones de credenciales en esta etapa.

## Evidencias

Los JSON y textos de consola se guardarán como registros automáticos reales.
Las capturas se solicitarán al estudiante en el momento de la ejecución y no
se presentará un registro textual como sustituto de una captura. No hace falta
capturar todos los comandos de preparación. Antes de continuar tras una
solicitud de captura se esperará la confirmación de que fue guardada.
El estudiante indicó continuar antes de confirmar la primera captura; por ello
se avanzó con la auditoría de lectura y se mantuvieron explícitamente
pendientes las evidencias faltantes, sin cerrar las preguntas.
Durante ese trabajo se recibió y verificó visualmente la captura de la primera
pregunta. Después el estudiante delegó la toma de capturas; la segunda se
obtuvo automáticamente de una ventana real de ejecución y también se verificó.

## Avance comprobado

- Preparación completada: copia UTF-8 válida, original intacto e igualdad de
  todos los campos. Commit `d2f184e` publicado y comprobado en GitHub.
- Pregunta 1: base independiente y tablas cargadas con 9.994 filas cada una;
  209.874 valores comparados satisfactoriamente. Captura del estudiante
  recibida, verificada e incorporada al repositorio.
- Pregunta 2: auditoría ejecutada y contrastada con el CSV. Se verificaron
  5.009 órdenes y 793 clientes, sin incumplimientos en los controles requeridos.
  Captura de la ejecución real obtenida con autorización e inspeccionada.
- Preguntas 3 a 8: pendientes; no se generaron resultados anticipados.
- Ante la proximidad de entrega se detuvo el desarrollo adicional y se
  priorizó publicar el trabajo comprobado; véase `estado_entrega.md`.
