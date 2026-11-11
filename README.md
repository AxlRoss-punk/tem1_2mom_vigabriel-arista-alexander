# Sample Superstore: práctica individual de Apache Hive

Repositorio: `tem1_2mom_vigabriel-arista-alexander`.

El objetivo es implementar y comprobar en Apache Hive el almacenamiento, la
calidad de datos y los análisis de las ocho preguntas del examen práctico
individual del segundo momento. La consigna menciona también doce scripts;
esa discrepancia queda pendiente de consulta al docente.

## Entorno

Windows 11, PowerShell, WSL2 Ubuntu, Docker Desktop, Docker Compose,
Apache Hive 4.0.1, HDFS, Beeline, Git y Python 3 en Ubuntu. El proyecto Docker
existente está en `/home/dante/LI16_Apache_Hive/docker-hadoop-hive-parquet`.

## Documentación

- [Inspección inicial](documentacion/analisis_dataset.md).
- [Registro previo de preparación y GitHub](documentacion/preparacion_entorno.md).
- [Plan por bloques y declaración de uso de IA](documentacion/plan_ejecucion.md).
- [Diccionario de datos](documentacion/diccionario_datos.md).
- [Pregunta 1: modelo, carga y resultados verificados](documentacion/p01_modelo_carga.md).
- [Pregunta 2: auditoría de calidad y resultados verificados](documentacion/p02_auditoria_calidad.md).
- [Evidencias](evidencias/README.md).

## Preparación del dataset

Desde la raíz del repositorio en PowerShell:

```powershell
wsl -d Ubuntu -- python3 -B scripts/preparar_dataset.py --source "/mnt/c/Users/dante/Downloads/Sample - Superstore.csv"
```

El script crea `datos/preparados/superstore_utf8.csv` y el registro
`evidencias/preparacion_ingesta.json`. Rechaza destinos existentes y nunca
sobrescribe el original. Conserva la cabecera, los finales de línea, las
comillas, los códigos postales y todos los valores; únicamente recodifica a
UTF-8 sin BOM. La copia se excluye de Git.

El registro permite comprobar 9.994 filas de datos, 21 columnas, igualdad de
todos los campos y el hash invariable del original. Si los destinos ya
existen, no repetir la preparación: consultar y verificar el registro previo.

## Estado y condiciones

La preparación está verificada y publicada. La pregunta 1 tiene ambas tablas
cargadas con 9.994 registros y una comparación satisfactoria de los 209.874
valores. La pregunta 2 tiene la auditoría ejecutada y contrastada: 5.009 órdenes
únicas, 793 clientes y cero incumplimientos en los controles requeridos.
La captura de la pregunta 1 está recibida y verificada; la de la pregunta 2
continúa pendiente. Las preguntas 3 a 8 no se han ejecutado todavía.

Para mostrar los conteos reales en una tabla y tomar la captura:

```powershell
wsl -d Ubuntu -- python3 -B scripts/mostrar_carga.py
```

Para mostrar el resumen real de auditoría sin modificar datos ni archivos:

```powershell
wsl -d Ubuntu -- python3 -B scripts/auditar_calidad.py --mostrar
```

Los scripts HiveQL de la pregunta 2 son `04_p02_resumen.sql`,
`05_p02_nulls.sql` y `06_p02_incidencias.sql`. Los registros automáticos se
guardan en `evidencias/p02_*`; son salidas reales de consola y verificaciones,
no capturas del estudiante.

La carga inicial está en `scripts/cargar_superstore.py`; rechaza una segunda
ejecución sobre la base existente. Las preguntas solo se declararán terminadas
tras su ejecución y sus evidencias.
No se modificarán las bases `db_alexander`, `dbec_alexander`, `db3_alexander`
ni `db4_alexander`.

El estudiante confirmó autorización docente para desarrollar soluciones con
IA. Se declara su uso como apoyo técnico; la comprensión del código, la
revisión y las interpretaciones finales corresponden al estudiante.
