# Configuración del entorno y del repositorio

## Entorno utilizado

La práctica utiliza Windows 11, PowerShell, WSL2 Ubuntu, Docker Desktop,
Apache Hive 4.0.1, HDFS y Beeline. El proyecto Docker existente está en
`/home/dante/LI16_Apache_Hive/docker-hadoop-hive-parquet`.

La conexión utilizada es:

```text
jdbc:hive2://localhost:10000/default
```

La configuración consultada indicó `fs.defaultFS=hdfs://namenode:8020`.
Los datos de Superstore se ubicaron en una ruta propia; las bases anteriores
se mantuvieron separadas.

## Repositorio y autenticación

Repositorio remoto:
<https://github.com/AxlRoss-punk/tem1_2mom_vigabriel-arista-alexander>.

Se utilizó Git 2.55.0 y Git Credential Manager 2.9.1. El acceso de escritura se
comprobó con la cuenta `AxlRoss-punk`. La identidad del autor de los commits
se mantuvo como Alexander Vigabriel.

La selección del helper se estableció únicamente en la configuración local:

```powershell
git --% config --local --replace-all credential.helper ""
git config --local --add credential.helper manager
```

El argumento vacío reinicia la lista de helpers para este repositorio; no
elimina credenciales guardadas. No se cambiaron opciones globales ni se
incluyeron secretos en los archivos de la práctica.

La publicación se comprobó comparando el SHA de `main` con
`git ls-remote origin refs/heads/main`. El historial conserva los hitos de
preparación, modelo, auditoría, consultas y documentación.

## Incidencias técnicas

- La consulta del almacén de credenciales desde el entorno restringido falló;
  se repitió con acceso autorizado al almacén de Windows.
- El error inicial de obtención de credenciales se resolvió seleccionando GCM
  expresamente y conservando esa selección solo para el repositorio.
- Hubo advertencias de acceso al archivo global de exclusiones dentro del
  entorno restringido. No se modificó su contenido ni sus permisos.
- La opción temporal `core.excludesFile=NUL` fue rechazada y se descartó.
- Beeline emitió avisos por varias implementaciones SLF4J y por
  `/home/hive/.beeline`; las consultas verificadas terminaron con código 0.

## Integridad de los datos

El CSV original se leyó sin modificarlo. La copia UTF-8 está excluida de Git y
su proceso de creación se explica en el README. Los hashes y la comparación
de campos están en `evidencias/preparacion_ingesta.json`.

La ingesta distingue una tabla externa textual de una tabla analítica con
tipos explícitos. El modelo, los comandos de carga y los resultados se
documentan en [pregunta 1](p01_modelo_carga.md). Los controles posteriores se
documentan en [pregunta 2](p02_auditoria_calidad.md).
