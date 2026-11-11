# Resultados ejecutados de las preguntas 3 a 8

Estos resultados proceden de consultas reales sobre
`superstore_alexander_2mom.superstore`. Las trece consultas de resultados
terminaron con código 0 y fueron contrastadas con el CSV original mediante
61.428 comprobaciones. Véase [verificación](../evidencias/analitica_verificacion.json).
Los registros y TSV conservan las salidas originales de Beeline.

## Pregunta 3 — evolución comercial por región

**Enunciado:** ventas y ganancias por región y año, margen, variación anual e
identificación de mejor y peor desempeño mediante CTE y ventanas.

**Estrategia y HiveQL:** [evolución anual](../scripts/07_p03_evolucion.sql) y
[ranking regional](../scripts/08_p03_regiones.sql). Se agrega antes de aplicar
`LAG`. Margen = 100 × ganancia / ventas. Variación de ventas utiliza ventas
previas; la de ganancia utiliza el valor absoluto de la ganancia previa para
conservar el sentido de mejora cuando la base sea negativa. Sin antecedente o
con denominador cero se devuelve NULL. El desempeño se ordena por ganancia.

| Región | Ventas acumuladas | Ganancia acumulada | Margen % |
|---|---:|---:|---:|
| West | 725457.8245 | 108418.4489 | 14.9448 |
| East | 678781.2400 | 91522.7800 | 13.4834 |
| South | 391721.9050 | 46749.4303 | 11.9343 |
| Central | 501239.8908 | 39706.3625 | 7.9216 |

**Resultado y evidencia:** las 16 combinaciones región/año de 2014–2017 están
en [TSV anual](../evidencias/07_p03_evolucion.tsv), incluido el margen y ambas
variaciones. [Captura real](../evidencias/p03_evolucion.png), inspeccionada.

**Interpretación y conclusión técnica:** West presenta la mayor ganancia total
y Central la menor. Central vende más que South, pero obtiene menos ganancia;
el volumen facturado por sí solo no identifica el mejor desempeño.

## Pregunta 4 — segmentación RFM

**Enunciado:** recencia con la fecha máxima del dataset, frecuencia de órdenes
únicas, ventas acumuladas, puntuaciones y segmentos justificados.

**Estrategia y HiveQL:** [clientes](../scripts/09_p04_clientes.sql) y
[segmentos](../scripts/10_p04_segmentos.sql). Referencia: **2017-12-30**.
R = días desde la última compra; F = órdenes distintas; M = suma de ventas.
`NTILE(5)` asigna puntuaciones 1–5: mayor puntuación corresponde a menor
recencia y mayor frecuencia/importe. `customer_id` desempata de forma
determinista; valores iguales pueden quedar en quintiles contiguos.

La prioridad de clasificación es: alto valor si R,F,M ≥ 4; en riesgo si R ≤ 2
y F o M ≥ 3; recurrentes si F ≥ 4 entre los restantes; recientes si R ≥ 4 y
F ≤ 2; otros en los demás casos. Los segmentos son excluyentes y relativos a
esta población, no predicciones de abandono.

| Segmento | Clientes | Ventas acumuladas |
|---|---:|---:|
| En riesgo | 201 | 693276.3569 |
| Alto valor | 104 | 553088.7041 |
| Otros | 269 | 522254.1464 |
| Recurrentes | 131 | 369192.2211 |
| Recientes | 88 | 159389.4318 |

**Resultado y evidencia:** [793 clientes con sus puntuaciones](../evidencias/09_p04_clientes.tsv)
y [resumen real](../evidencias/10_p04_segmentos.tsv). Captura PNG pendiente.

**Interpretación y conclusión técnica:** el grupo en riesgo acumula un importe
histórico relevante y merece revisión comercial; su clasificación refleja
recencia baja en puntuación y antecedentes de frecuencia o importe elevados.
La política de quintiles debe revisarse si se requieren umbrales absolutos.

## Pregunta 5 — ranking de productos

**Enunciado:** cinco productos de mayor ganancia por categoría, mayor volumen
de ventas y menor rentabilidad; margen individual, posición, `RANK`,
`DENSE_RANK` y agregaciones acumulativas.

**Estrategia y HiveQL:** [ranking completo](../scripts/11_p05_productos.sql),
[selecciones](../scripts/12_p05_seleccion.sql) y
[volumen físico](../scripts/21_p05_volumen_unidades.sql). Se agrupa por
categoría e identificador; `MIN(product_name)` es solo una etiqueta y se cuenta
la cantidad de nombres distintos. El margen es ganancia/ventas, en porcentaje.
Se incluyen volumen monetario y unidades, además de los cinco peores por
ganancia absoluta y por margen. Son criterios distintos de desempeño.

`RANK` conserva saltos ante empates y `DENSE_RANK` no; ambos se publican. Para
entregar exactamente cinco productos se usa `ROW_NUMBER`, con identificador
como desempate. Los acumulados por categoría usan una ventana `ROWS` ordenada
por ganancia descendente e identificador.

**Resultados reales:** 1.862 productos agregados. El producto
`TEC-CO-10004722` lidera las ventas monetarias con 61599.8240 y obtiene
25199.9280 de ganancia. `TEC-MA-10000418` presenta la menor ganancia acumulada,
-8879.9704. El menor margen corresponde a `OFF-AP-10002203`, -275.0000%, sobre
ventas de 1.6240; ese porcentaje no representa la mayor pérdida absoluta.
Por unidades, lidera `TEC-AC-10003832` con 75.

**Evidencia:** [ranking y acumulados](../evidencias/11_p05_productos.tsv),
[cinco por criterio, incluidos quince por categoría](../evidencias/12_p05_seleccion.tsv)
y [cinco por unidades](../evidencias/21_p05_volumen_unidades.tsv).
Captura PNG pendiente.

**Interpretación y conclusión técnica:** facturación, unidades, ganancia y
margen responden a preguntas diferentes. Los resultados permiten distinguir
productos de alta facturación que no generan beneficios de los que aportan
mayor ganancia. Los identificadores con varios nombres requieren revisión de
catálogo antes de interpretar su etiqueta como una identidad inequívoca.

## Pregunta 6 — descuentos y rentabilidad

**Enunciado:** rangos 0, (0;20%], (20%;50%] y >50%; ventas, ganancias, margen,
pérdidas, porcentaje no rentable, descuento promedio y categorías afectadas.

**Estrategia y HiveQL:** [rangos](../scripts/13_p06_rangos.sql) y
[categorías/subcategorías](../scripts/14_p06_subcategorias.sql). Una pérdida
significa `profit < 0`; no rentable significa `profit <= 0`, incluyendo
equilibrio. El descuento promedio es una media por línea, sin ponderar por
importe. La afectación se ordena por pérdida bruta: suma de pérdidas absolutas.

| Rango | Líneas | Ganancia | Margen % | No rentables % |
|---|---:|---:|---:|---:|
| Sin descuento | 4798 | 320987.6032 | 29.5050 | 0.6253 |
| Bajo | 3803 | 100785.4745 | 11.9058 | 14.3308 |
| Medio | 537 | -58817.0047 | -19.7015 | 94.0410 |
| Alto | 856 | -76559.0513 | -119.1975 | 100.0000 |

**Resultado y evidencia:** [todas las métricas por rango](../evidencias/13_p06_rangos.tsv)
y [detalle por categoría y subcategoría](../evidencias/14_p06_subcategorias.tsv).
Binders con descuento alto acumula -38510.4964 de ganancia; Tables con
descuento medio, -30698.2228. Captura PNG pendiente.

**Interpretación y conclusión técnica:** los descuentos altos se asocian con
mayor proporción de operaciones no rentables en este dataset: las 856 líneas
del rango alto tienen pérdidas. Esta asociación observacional no prueba
causalidad; categorías y mezcla de productos también influyen.

## Pregunta 7 — tendencias temporales mensuales

**Enunciado:** ventas y ganancias mensuales, variación mensual e interanual,
promedio móvil de tres meses y los tres meses de mayores y menores ventas.

**Estrategia y HiveQL:** [serie](../scripts/15_p07_mensual.sql) y
[extremos](../scripts/16_p07_extremos.sql). Se construye un calendario completo
entre el mínimo y máximo mes, con capacidad de 120 meses comprobada para los
48 observados. Se agregan año y mes explícitos. `LAG(1)` y `LAG(12)` comparan
meses contiguos y el mismo mes anterior. La media móvil exige tres meses:
los dos iniciales son NULL, al igual que las comparaciones sin antecedente.

| Grupo | Mes | Ventas |
|---|---|---:|
| Mayor 1 | 2017-11 | 118447.8250 |
| Mayor 2 | 2016-12 | 96999.0430 |
| Mayor 3 | 2017-09 | 87866.6520 |
| Menor 1 | 2014-02 | 4519.8920 |
| Menor 2 | 2015-02 | 11951.4110 |
| Menor 3 | 2014-01 | 14236.8950 |

**Resultado y evidencia:** [48 meses con todas las variaciones y medias](../evidencias/15_p07_mensual.tsv)
y [extremos comprobados](../evidencias/16_p07_extremos.tsv). Captura PNG pendiente.

**Interpretación y conclusión técnica:** noviembre de 2017 lidera las ventas;
los mínimos observados se concentran al inicio de los primeros años. Estos
extremos justifican estudiar estacionalidad, sin demostrar por sí solos una
regla estacional generalizable.

## Pregunta 8 — Pareto de ventas y rentabilidad

**Enunciado:** análisis independientes de productos que acumulan el 80% de
ventas y ganancias, participación individual, acumulados y comparación.

**Estrategia y HiveQL:** [contribuciones](../scripts/17_p08_pareto.sql) y
[resumen](../scripts/18_p08_resumen.sql). Se ordena por aporte descendente,
desempatando por identificador. El corte es el primer prefijo cuyo acumulado
alcanza al menos 80%, incluyendo el producto que cruza el umbral.

| Análisis | Total | Productos para 80% | % de productos | % alcanzado |
|---|---:|---:|---:|---:|
| Ventas | 2297200.8603 | 414 | 22.2342 | 80.0370 |
| Ganancia neta | 286397.0217 | 164 | 8.8077 | 80.0303 |

**Resultado y evidencia:** [participación y acumulado de todos los productos](../evidencias/17_p08_pareto.tsv)
y [cortes reales](../evidencias/18_p08_resumen.tsv). Captura PNG pendiente.

**Interpretación y conclusión técnica:** la ganancia neta se concentra en una
fracción menor de productos que las ventas. Se conservaron los 299 productos
de ganancia negativa; por ello, el acumulado porcentual de ganancia puede
superar 100% antes de incorporar las pérdidas. El denominador es la ganancia
neta total positiva. La regla 80/20 es una referencia aproximada y no se fuerza
un corte exactamente igual al 20% de productos.

## Reproducción y límites del cierre

```powershell
wsl -d Ubuntu -- python3 -B scripts/ejecutar_analitica.py --bloque todos
```

El ejecutor conserva salidas y registra código de retorno, hash del SQL y del
resultado, tiempo y comando. Si ya existen, valida los hashes y no sobrescribe.
`verificar_analitica.py` ya produjo el informe final; protege los registros
existentes contra sobrescritura. Las cabeceras calificadas de Hive se
normalizan únicamente al leer para verificar, sin editar los TSV originales.

La comprobación detectó y corrigió una agrupación mensual incorrecta con
`TRUNC`; el intento descartado está en `evidencias/intento_inicial_p07/` y no
es el resultado válido. Las salidas finales de P7 contienen los 48 meses y
pasaron la comparación independiente. La captura de P4 se interrumpió porque
su ventana no estaba delante; no se generó una imagen de otra aplicación ni
se incorporó una captura que no mostrara el resultado previsto.

Las capturas PNG de P4 a P8 permanecen pendientes. Los resultados y registros
de consola de las seis preguntas están ejecutados y comprobados. Los criterios
de cálculo y las limitaciones quedan indicados para interpretar cada resultado.

Los archivos `p05_captura.sql`, `p06_captura.sql` y `p07_captura.sql` son
auxiliares preparados para visualizar proyecciones de los resultados; no se
presentan como capturas realizadas ni como nuevas ejecuciones verificadas.
