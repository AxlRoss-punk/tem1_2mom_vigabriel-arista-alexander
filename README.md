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

La preparación se documenta con verificaciones reales. La carga en Hive y las
preguntas solo se declararán terminadas tras su ejecución y sus evidencias.
No se modificarán las bases `db_alexander`, `dbec_alexander`, `db3_alexander`
ni `db4_alexander`.

El estudiante confirmó autorización docente para desarrollar soluciones con
IA. Se declara asistencia de Codex; la comprensión del código, la revisión y
las interpretaciones finales corresponden al estudiante.
