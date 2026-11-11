# Práctica individual de Apache Hive — Sample Superstore

**Estudiante:** Alexander Vigabriel

**Evaluación:** Examen práctico individual, segundo momento

**Dataset:** Sample Superstore, 9.994 registros y 21 columnas

## Objetivo

Construir un proceso de ingesta, modelado y análisis de datos con Apache Hive.
La práctica comprende la revisión del CSV, la creación de una tabla analítica,
la auditoría de calidad y la resolución de consultas comerciales mediante
agregaciones, CTE y funciones de ventana.

## Entorno de trabajo

Windows 11, PowerShell, WSL2 Ubuntu, Docker Desktop, Docker Compose, Apache
Hive 4.0.1, HDFS, Beeline, Git y Python 3. El proyecto Docker se encuentra en
`/home/dante/LI16_Apache_Hive/docker-hadoop-hive-parquet`.

La base de esta práctica es `superstore_alexander_2mom`. Se mantuvieron
separadas las bases de las prácticas anteriores.

## Organización del repositorio

| Carpeta | Contenido |
|---|---|
| `scripts/` | Preparación, DDL, carga, consultas HiveQL y verificaciones |
| `documentacion/` | Diccionario, metodología, resultados y conclusiones |
| `evidencias/` | Salidas de consola, TSV, comprobaciones y capturas disponibles |
| `datos/` | Copia de trabajo local, excluida del versionado |

## Procedimiento de ejecución

Los comandos siguientes se ejecutan desde la raíz del repositorio en
PowerShell. El CSV original se conserva sin modificaciones.

**Preparación inicial del dataset:**

```powershell
wsl -d Ubuntu -- python3 -B scripts/preparar_dataset.py --source "/mnt/c/Users/dante/Downloads/Sample - Superstore.csv"
```

Se obtiene una copia UTF-8 sin BOM y un registro de integridad. El script
rechaza sobrescribir archivos existentes.

**Creación del modelo y carga inicial:**

```powershell
wsl -d Ubuntu -- python3 -B scripts/cargar_superstore.py
```

Este paso ya se realizó. El ejecutor comprueba que el nombre de base y la
ruta de carga estén libres y rechaza repetir la carga sobre lo existente.

**Consulta de los resultados de carga y auditoría:**

```powershell
wsl -d Ubuntu -- python3 -B scripts/mostrar_carga.py
wsl -d Ubuntu -- python3 -B scripts/auditar_calidad.py --mostrar
```

**Ejecución o comprobación de los bloques analíticos:**

```powershell
wsl -d Ubuntu -- python3 -B scripts/ejecutar_analitica.py --bloque todos
```

Los resultados existentes se conservan y sus hashes se verifican. Los informes
de comprobación ya generados están en `evidencias/`.

## Resultados principales

- Se cargaron 9.994 filas en las capas textual y analítica, conservando los
  209.874 valores del archivo.
- La auditoría identificó 5.009 órdenes y 793 clientes; los controles requeridos
  no detectaron duplicados de fila, NULL ni inconsistencias numéricas o de fechas.
- Las preguntas 3 a 8 se ejecutaron y contrastaron con 61.428 comprobaciones.
- Se midieron consultas equivalentes sobre CSV y ORC, con igualdad de resultados.
- Hay capturas de las preguntas 1 a 3. Las capturas de las preguntas 4 a 8
  permanecen pendientes; sus resultados y registros de ejecución están disponibles.

## Documentación de la práctica

1. [Inspección del dataset](documentacion/analisis_dataset.md).
2. [Diccionario de datos](documentacion/diccionario_datos.md).
3. [Metodología y alcance](documentacion/plan_ejecucion.md).
4. [Configuración del entorno](documentacion/preparacion_entorno.md).
5. [Pregunta 1: modelo y carga](documentacion/p01_modelo_carga.md).
6. [Pregunta 2: auditoría](documentacion/p02_auditoria_calidad.md).
7. [Preguntas 3 a 8: resultados e interpretación](documentacion/p03_p08_resultados.md).
8. [Optimización medida](documentacion/optimizacion.md).
9. [Conclusiones](documentacion/conclusiones.md).
10. [Resumen de entregables y pendientes](documentacion/estado_entrega.md).
11. [Índice de evidencias](evidencias/README.md).

La consigna desarrolla ocho preguntas y menciona doce scripts en sus requisitos.
Se resolvieron las ocho preguntas enunciadas; la diferencia queda identificada
en la metodología.
