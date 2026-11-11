# Preparación del entorno y registro de intervención

Fecha: 11 de noviembre de 2026 (America/Caracas).

Alcance: autenticación de GitHub, comprobación de la estructura local y
planificación de la ingesta de Sample Superstore. Este documento registra
asistencia técnica de Codex; no contiene respuestas ni consultas de las
preguntas evaluadas. No se encontró una política docente en los archivos
disponibles: las condiciones específicas deberán contrastarse con la consigna
antes de preparar entregables evaluados.

## 1. Estado inicial comprobado

- Repositorio local: `C:\Users\dante\Practicas_Apache_Hive\tem1_2mom_vigabriel-arista-alexander`.
- Repositorio remoto: <https://github.com/AxlRoss-punk/tem1_2mom_vigabriel-arista-alexander>.
- Rama local: `main`, inicialmente un commit por delante de `origin/main`.
- Commit solicitado: `b42c1abace2ea905cd9ffde20dd85bcd8bc99f09`,
  `docs: analisis inicial del dataset Superstore`.
- Referencia remota inicial, comprobada mediante la API de GitHub:
  `dc238d07d0d086ec5c465092df017c4273e01525`.
- Git instalado: `2.55.0.windows.5`.
- Git Credential Manager (GCM): `2.9.1`.
- El helper configurado a nivel de sistema es `manager`.
- `origin` ya especificaba el usuario `AxlRoss-punk` en su URL HTTPS;
  no contenía un componente de contraseña.
- GCM enumeró las cuentas `AxlRoss-punk` y `AlexVigabriel`.
- No se encontraron archivos `AGENTS.md` en las ubicaciones comprobadas.

## 2. Registro de GitHub

1. Se revisaron el estado, el commit pendiente, las referencias locales, la
   configuración pertinente y la ayuda de GCM, evitando imprimir secretos.
2. La consulta de cuentas falló dentro del entorno restringido con
   `Unable to persist credentials with the 'wincredman' credential store`.
   Repetida fuera de él, con autorización, enumeró las dos cuentas.
3. Un intento de publicación con la interacción desactivada falló con
   `fatal: unable to get password from user`. En esta sesión no se reprodujo
   el error 403 comunicado por el usuario.
4. El usuario autorizó explícitamente iniciar sesión por navegador y guardar o
   renovar exclusivamente la credencial de `AxlRoss-punk`.
5. GCM indicó inicialmente que esa cuenta ya tenía credenciales. Se ejecutó
   entonces su inicio de sesión por navegador con `--force` para la cuenta
   autorizada; el proceso terminó con código 0. Un nuevo intento de publicación
   sin seleccionar explícitamente el helper volvió a fallar.
6. Se obtuvo la credencial mediante GCM únicamente en memoria. La API de GitHub
   confirmó la identidad `AxlRoss-punk`, el repositorio esperado y el permiso
   `push`. No se imprimió ni se escribió el token en archivos.
7. La publicación tuvo éxito al seleccionar GCM expresamente para ese comando:

   ```powershell
   git -c credential.helper= -c credential.helper=manager -c credential.interactive=false push origin main
   ```

   Git informó: `dc238d0..b42c1ab main -> main`.
   Las opciones `-c` se aplicaron solo al proceso; no modificaron la
   configuración global ni local. El valor vacío reinicia la lista de helpers
   para ese comando; no borra credenciales guardadas.
8. Una simulación sin seleccionar el helper expresamente volvió a fallar. Para
   resolver también las publicaciones futuras, se configuró exclusivamente
   `.git/config` con un reinicio local de la lista de helpers y `manager`:

   ```powershell
   git --% config --local --replace-all credential.helper ""
   git config --local --add credential.helper manager
   ```

   `--%` permite pasar el argumento vacío desde Windows PowerShell 5.1.
   No se cambiaron valores globales ni se eliminaron credenciales. La URL de
   `origin`, que ya identifica a `AxlRoss-punk`, se mantuvo.
9. La verificación final mediante `git ls-remote origin refs/heads/main`
   devolvió `b42c1abace2ea905cd9ffde20dd85bcd8bc99f09`, igual que `main` y
   `origin/main` locales. La simulación de publicación con la interacción
   desactivada terminó correctamente con `Everything up-to-date`.

Durante las comprobaciones iniciales de estado apareció además una advertencia
de permisos al consultar `C:\Users\dante\.config\git\ignore` dentro del entorno
restringido. No impidió inspeccionar el repositorio; no se modificó ese archivo
ni se cambiaron sus permisos. La verificación final fuera de ese entorno no
mostró esa advertencia.

Una comprobación de estado que intentó omitir esa advertencia mediante la
opción temporal `core.excludesFile=NUL` falló con
`fatal: cannot use NUL as an exclude file`. Se descartó esa opción y se repitió
la consulta habitual; no se guardó ningún cambio en la configuración de
exclusiones.

No se ejecutaron `logout`, `erase`, `credential reject`, cambios de autor,
reescrituras de historial ni publicaciones forzadas. La opción `--force`
anterior correspondió al inicio de sesión autorizado, no a `git push`.

## 3. Estructura del proyecto

| Elemento | Comprobación local | Estado versionado al inicio |
|---|---|---|
| `README.md` | Existe | Incluido en `b42c1ab` |
| `documentacion/analisis_dataset.md` | Existe; contiene la inspección inicial | Incluido en `b42c1ab` |
| `scripts/` | Existe y está vacío | Sin archivos versionados |
| `evidencias/` | Existe y está vacío | Sin archivos versionados |

Git no conserva directorios vacíos. Para que las dos carpetas aparezcan en
GitHub será necesario incorporar posteriormente un archivo pertinente o un
marcador como `.gitkeep`. En esta intervención no se añadieron esos marcadores.

## 4. CSV original: revisión de solo lectura

- Ruta: `C:\Users\dante\Downloads\Sample - Superstore.csv`.
- Tamaño: 2.287.806 bytes.
- SHA-256 de referencia:
  `58FB59C63089E564D835E4AABE19D371757DE1137A5BF1888243AE386C4B7A97`.
- Registros de datos: 9.994; columnas: 21; cabecera presente.
- Cero registros con una cantidad incorrecta de campos.
- UTF-8 original no válido; Windows-1252 es la identificación inferida de los
  bytes, no una declaración explícita del archivo.
- Separador: coma; delimitador de texto: comilla doble; comillas literales
  escapadas mediante duplicación.
- 2.221 nombres de productos con comas y 811 con comillas literales.
- No se detectaron saltos de línea dentro de campos.
- Todas las fechas son válidas como `M/d/yyyy`.
- `Sales` y `Profit`: hasta cuatro decimales; `Discount`: hasta dos.
  Hay 1.871 registros con beneficios negativos.
- No se encontraron campos vacíos ni los marcadores comprobados `NULL`, `\N`,
  `N/A`, `NA`, `None` o `NaN`, sin distinguir mayúsculas.
- 438 códigos postales tienen cuatro dígitos; 11 registros conservan un cero
  inicial. La supuesta pérdida de ceros en los primeros requiere validación.
- 225 nombres de productos contienen espacios no separables `U+00A0` y 16
  presentan espacios en los extremos.

## 5. Siguiente etapa: recomendaciones, todavía no ejecutadas

1. **Preservar el origen.** Registrar su hash y generar, en una etapa posterior,
   una copia derivada en UTF-8, preferiblemente sin BOM. No sobrescribir el CSV
   original. La conversión debe ser estricta y conservar los caracteres; no
   sustituir comillas tipográficas ni espacios silenciosamente.
2. **Comprobar la copia.** Decodificarla estrictamente como UTF-8 y comparar sus
   9.994 registros y sus 21 valores por registro con el origen decodificado
   como Windows-1252. El hash de la copia cambiará por la recodificación; el del
   original deberá permanecer igual. CRLF es el final de línea original;
   cualquier normalización a LF debe quedar registrada.
3. **Interpretar CSV.** Conservar las comillas que protegen comas internas y la
   duplicación de comillas literales. No usar una separación simple por comas.
   Validar casos con comas y con dimensiones como `72""H`.
4. **Separar cabecera y datos.** Elegir una única estrategia: retirar la cabecera
   solamente de la copia derivada o configurar su omisión en la lectura. No
   aplicar ambas estrategias, pues se perdería el primer registro de datos.
5. **Preparar una zona de carga textual.** Si se elige `OpenCSVSerde`, planificar
   las 21 columnas iniciales como `STRING`: la documentación de Apache indica
   que ese SerDe entrega cadenas y no admite saltos de línea dentro de campos.
   Después se convertirán los valores a los tipos de destino.
   [Documentación de CSV SerDe](https://hive.apache.org/docs/latest/user/csv-serde/).
6. **Convertir con reglas explícitas.** Interpretar las fechas como mes/día/año
   y representarlas posteriormente como `DATE`; no asumir que una conversión
   directa desde `M/d/yyyy` reconoce el formato. Utilizar `INT` para `Row ID` y
   `Quantity`, `DECIMAL(12,4)` para `Sales` y `Profit`, `DECIMAL(3,2)` para
   `Discount` y `STRING` para los identificadores y demás textos, incluido
   `Postal Code`. Conservar las pérdidas como valores negativos.
   [Tipos de Hive](https://hive.apache.org/docs/latest/language/languagemanual-types/).
7. **Conservar y justificar la limpieza.** Mantener los códigos postales
   originales como texto. Validar antes de completar ceros iniciales. Cualquier
   recorte de espacios o sustitución de `U+00A0` debe aplicarse solo sobre datos
   derivados y registrar su alcance.
8. **Aislar la ingesta.** Confirmar antes de cargar la base de datos y la ruta de
   almacenamiento autorizadas para esta práctica. No reutilizar ni alterar las
   bases LI16, LI17, LI18 o LI19. Identificar por separado las rutas de Windows,
   WSL, el contenedor y HDFS; no asumir que una ruta local existe en todos ellos.
9. **Verificar después de cargar.** Confirmar 9.994 registros de datos,
   alineación de las 21 columnas, ausencia de cabecera como fila y ausencia de
   nuevos valores nulos por errores de conversión. Contrastar los casos de
   comillas, fechas no ambiguas, códigos con cero inicial y decimales con cuatro
   posiciones con el origen. Estos son criterios de validación de ingesta;
   no se prepararon consultas de las preguntas evaluadas.

## 6. Cambios realizados y límites

- Se creó este documento para registrar pasos, resultados y recomendaciones.
- Se publicó únicamente el commit previamente solicitado; no se crearon
  nuevos commits para esta documentación.
- Se añadió únicamente la selección del helper en `.git/config`, con valores
  locales vacío y `manager`. Esta configuración no se publica con los commits.
- La configuración global y las credenciales de `AlexVigabriel` no fueron
  modificadas por acciones explícitas de esta intervención.
- Se autorizó y ejecutó la renovación de la credencial de `AxlRoss-punk`.
- No se modificaron `README.md` ni `documentacion/analisis_dataset.md`.
- No se ejecutaron Docker, Hive, Beeline, cambios de bases de datos,
  eliminación de contenedores o volúmenes ni transformaciones del CSV.
- El hash SHA-256 del CSV se comprobó de nuevo y coincide con el de referencia:
  el original permanece sin cambios.
- GitHub, `main` y `origin/main` coinciden en el commit solicitado. Este nuevo
  documento permanece local y sin seguimiento; no fue añadido al índice ni
  incluido en una publicación adicional.

Referencia para el uso de varias cuentas:
[Git Credential Manager: Multiple users](https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/multiple-users.md).
