
# Análisis inicial del dataset — Sample Superstore

## 1. Identificación del dataset

- Nombre: Sample Superstore
- Fuente: Kaggle
- URL: https://www.kaggle.com/datasets/vivek468/superstore-dataset-final
- Archivo original: Sample - Superstore.csv
- Registros de datos: 9994
- Columnas: 21

## 2. Estructura del archivo

- Separador: coma (,)
- Delimitador de texto: comilla doble (")
- Codificación más probable: Windows-1252
- UTF-8 original: no válido
- Encabezado: presente
- Finales de línea: CRLF

## 3. Fechas y valores numéricos

- Order Date: formato M/d/yyyy
- Ship Date: formato M/d/yyyy
- Sales: valores decimales con hasta 4 posiciones
- Quantity: valores enteros
- Discount: valores decimales con hasta 2 posiciones
- Profit: valores decimales con hasta 4 posiciones, incluidos valores negativos

## 4. Características especiales

- 2221 nombres de productos contienen comas dentro de campos entrecomillados.
- 811 nombres de productos contienen comillas literales escapadas mediante comillas dobles.
- No se detectaron saltos de línea dentro de los campos.
- Se encontraron caracteres especiales y espacios no separables.
- Se identificaron 16 nombres de productos con espacios en los extremos.

## 5. Calidad inicial

- No se detectaron registros con cantidades incorrectas de columnas.
- No se detectaron campos vacíos.
- No se identificaron marcadores NULL explícitos entre los comprobados.
- Postal Code debe conservarse como texto.
- Existen 438 códigos postales con cuatro dígitos y 9556 con cinco dígitos.
- Algunos códigos de cuatro dígitos podrían haber perdido ceros iniciales previamente.

## 6. Precauciones para Apache Hive

1. Conservar el archivo CSV original sin modificaciones.
2. Utilizar un lector CSV que respete las comillas y las comas internas.
3. Convertir los datos a UTF-8 antes de la ingesta.
4. Interpretar explícitamente las fechas M/d/yyyy.
5. Almacenar Postal Code como STRING.
6. Verificar el número de registros después de importar.
7. Documentar las transformaciones realizadas.

## 7. Alcance de la inspección

Este documento recoge los resultados del análisis previo a la ingesta.

Los hallazgos proceden de la inspección técnica del CSV en modo lectura.
La identificación de Windows-1252 es una inferencia respaldada por los
bytes y caracteres observados, no una declaración explícita del archivo.

La auditoría analítica de calidad solicitada en la Pregunta 2 se realizará
posteriormente en Apache Hive.
