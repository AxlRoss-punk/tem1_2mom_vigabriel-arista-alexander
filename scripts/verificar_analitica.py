#!/usr/bin/env python3
"""Contrasta los resultados de Hive con cálculos independientes del CSV."""

import csv
import hashlib
import io
import json
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, getcontext

from cargar_superstore import ROOT
from ejecutar_analitica import GROUPS

getcontext().prec = 50
checks = 0


def require(condition, message):
    global checks
    if not condition:
        raise AssertionError(message)
    checks += 1


def number(value):
    return None if value in ('NULL', 'null', '', None) else Decimal(str(value))


def equal(actual, expected, message, tolerance=Decimal('0.00011')):
    a = number(actual)
    require(a is None if expected is None else a is not None and abs(a - Decimal(expected)) <= tolerance,
            message + ': ' + str(actual) + ' != ' + str(expected))


def pct(a, b):
    return None if b == 0 else Decimal(100) * a / b


def load(name):
    path = ROOT / 'evidencias' / (name + '.tsv')
    record = json.loads((ROOT / 'evidencias' / (name + '.ejecucion.json')).read_text())
    require(record['exit_code'] == 0, 'Código de salida ' + name)
    require(hashlib.sha256(path.read_bytes()).hexdigest() == record['output_sha256'], 'Hash resultado ' + name)
    require(hashlib.sha256((ROOT / record['sql_file']).read_bytes()).hexdigest() == record['sql_sha256'], 'Hash SQL ' + name)
    records = csv.DictReader(io.StringIO(path.read_text(encoding='utf-8')), delimiter='\t', quoting=csv.QUOTE_NONE)
    return [{key.rsplit('.', 1)[-1]: value for key, value in row.items()} for row in records]


def group(rows, key):
    groups = defaultdict(list)
    for row in rows:
        groups[key(row)].append(row)
    return groups


def totals(rows):
    return sum((r['sales'] for r in rows), Decimal(0)), sum((r['profit'] for r in rows), Decimal(0))


def ntile(items, key):
    ordered = sorted(items, key=key)
    size, remainder = divmod(len(ordered), 5)
    result = {}
    offset = 0
    for tile in range(1, 6):
        count = size + (tile <= remainder)
        for identifier in ordered[offset:offset + count]:
            result[identifier] = tile
        offset += count
    return result


def main():
    destination = ROOT / 'evidencias/analitica_verificacion.json'
    if destination.exists():
        raise FileExistsError('Se conserva la verificación existente.')
    preparation = json.loads((ROOT / 'evidencias/preparacion_ingesta.json').read_text())
    source = __import__('pathlib').Path(preparation['source'])
    data = source.read_bytes()
    require(hashlib.sha256(data).hexdigest() == preparation['source_sha256'], 'CSV original intacto')
    rows = list(csv.DictReader(io.StringIO(data.decode('cp1252'), newline=''), strict=True))
    for row in rows:
        for key in ('Sales', 'Profit', 'Discount'):
            row[key.lower()] = Decimal(row[key])
        row['date'] = datetime.strptime(row['Order Date'], '%m/%d/%Y').date()
        row['quantity'] = int(row['Quantity'])
    outputs = {name: load(name) for name in GROUPS['II'] + GROUPS['III']}

    annual = group(rows, lambda r: (r['Region'], r['date'].year))
    p3 = outputs['07_p03_evolucion']
    require(len(p3) == len(annual), 'Todas las regiones y años')
    for result in p3:
        region, year = result['region'], int(result['anio'])
        sales, profit = totals(annual[(region, year)])
        equal(result['ventas'], sales, 'Ventas regionales')
        equal(result['ganancia'], profit, 'Ganancia regional')
        equal(result['margen_pct'], pct(profit, sales), 'Margen regional')
        previous = annual.get((region, year - 1))
        ps, pp = totals(previous) if previous else (None, None)
        equal(result['var_ventas_pct'], None if ps is None else pct(sales - ps, ps), 'Variación anual ventas')
        equal(result['var_ganancia_pct'], None if pp is None else pct(profit - pp, abs(pp)), 'Variación anual ganancia')
        profits = sorted({totals(v)[1] for (reg, yr), v in annual.items() if yr == year}, reverse=True)
        equal(result['rk_ganancia'], profits.index(profit) + 1, 'Ranking regional anual')
    regional = group(rows, lambda r: r['Region'])
    for result in outputs['08_p03_regiones']:
        sales, profit = totals(regional[result['region']])
        equal(result['ventas'], sales, 'Ventas totales región')
        equal(result['ganancia'], profit, 'Ganancia total región')
        equal(result['margen_pct'], pct(profit, sales), 'Margen total región')

    customers = group(rows, lambda r: r['Customer ID'])
    reference = max(row['date'] for row in rows)
    cm = {identifier: {'recencia': (reference - max(r['date'] for r in items)).days,
                     'frecuencia': len({r['Order ID'] for r in items}), 'monetario': totals(items)[0]}
          for identifier, items in customers.items()}
    rs = ntile(cm, lambda k: (-cm[k]['recencia'], k))
    fs = ntile(cm, lambda k: (cm[k]['frecuencia'], k))
    ms = ntile(cm, lambda k: (cm[k]['monetario'], k))
    require(len(outputs['09_p04_clientes']) == len(cm), 'Todos los clientes RFM')
    segments = defaultdict(list)
    for result in outputs['09_p04_clientes']:
        identifier = result['customer_id']
        require(result['referencia'] == reference.isoformat(), 'Referencia RFM')
        for key in ('recencia', 'frecuencia', 'monetario'):
            equal(result[key], cm[identifier][key], 'Medida RFM ' + key)
        r, f, m = rs[identifier], fs[identifier], ms[identifier]
        for key, expected in (('r', r), ('f', f), ('m', m)):
            equal(result[key], expected, 'Puntuación RFM')
        segment = ('Alto valor' if r >= 4 and f >= 4 and m >= 4 else
                   'En riesgo' if r <= 2 and (f >= 3 or m >= 3) else
                   'Recurrentes' if f >= 4 else 'Recientes' if r >= 4 and f <= 2 else 'Otros')
        require(result['segmento'] == segment and result['rfm'] == f'{r}{f}{m}', 'Segmento y código RFM')
        segments[segment].append(cm[identifier])
    for result in outputs['10_p04_segmentos']:
        members = segments[result['segmento']]
        equal(result['clientes'], len(members), 'Clientes por segmento')
        equal(result['ventas'], sum(x['monetario'] for x in members), 'Monetario por segmento')

    products = group(rows, lambda r: (r['Category'], r['Product ID']))
    pm = {key: {'ventas': totals(items)[0], 'ganancia': totals(items)[1],
                'unidades': sum(r['quantity'] for r in items),
                'variantes_nombre': len({r['Product Name'] for r in items})}
          for key, items in products.items()}
    for values in pm.values():
        values['margen_pct'] = pct(values['ganancia'], values['ventas'])
    ranked = defaultdict(dict)
    for category in {key[0] for key in pm}:
        keys = sorted((key for key in pm if key[0] == category), key=lambda k: (-pm[k]['ganancia'], k[1]))
        distinct = sorted({pm[k]['ganancia'] for k in keys}, reverse=True)
        cumulative_sales = cumulative_profit = Decimal(0)
        for position, key in enumerate(keys, 1):
            cumulative_sales += pm[key]['ventas']; cumulative_profit += pm[key]['ganancia']
            ranked[key].update(top_categoria=position, dense_categoria=distinct.index(pm[key]['ganancia']) + 1,
                               rank_categoria=next(i + 1 for i, k in enumerate(keys) if pm[k]['ganancia'] == pm[key]['ganancia']),
                               ventas_acumuladas=cumulative_sales, ganancia_acumulada=cumulative_profit)
    for label, keyfn in (('top_ventas', lambda k: (-pm[k]['ventas'], k[1])),
                         ('peor_ganancia', lambda k: (pm[k]['ganancia'], k[1])),
                         ('peor_margen', lambda k: (pm[k]['ganancia'] / pm[k]['ventas'], k[1]))):
        for position, key in enumerate(sorted(pm, key=keyfn), 1):
            ranked[key][label] = position
    require(len(outputs['11_p05_productos']) == len(pm), 'Todos los productos')
    for result in outputs['11_p05_productos']:
        key = result['category'], result['product_id']
        for label, value in {**pm[key], **ranked[key]}.items():
            equal(result[label], value, 'Producto ' + label)
    selections = {('Top ganancia categoria', *key) for key in pm if ranked[key]['top_categoria'] <= 5}
    for tag, label in (('Top ventas', 'top_ventas'), ('Peor ganancia', 'peor_ganancia'), ('Peor margen', 'peor_margen')):
        selections.update((tag, *key) for key in pm if ranked[key][label] <= 5)
    require({(r['listado'], r['category'], r['product_id']) for r in outputs['12_p05_seleccion']} == selections,
            'Listados exactos de cinco productos y sus empates')
    volume_keys = sorted(pm, key=lambda k: (-pm[k]['unidades'], k[1]))[:5]
    volume_rows = outputs['21_p05_volumen_unidades']
    require(len(volume_rows) == 5, 'Cinco productos por volumen fisico')
    for position, result in enumerate(volume_rows, 1):
        key = volume_keys[position - 1]
        require((result['category'], result['product_id']) == key, 'Ranking por unidades')
        for label in ('unidades', 'ventas', 'ganancia'):
            equal(result[label], pm[key][label], 'Volumen fisico ' + label)

    def band(row):
        d = row['discount']
        return 'Sin descuento' if d == 0 else 'Bajo' if d <= Decimal('.2') else 'Medio' if d <= Decimal('.5') else 'Alto'

    def check_discount(result, members):
        sales, profit = totals(members)
        metrics = {'n': len(members), 'ventas': sales, 'ganancia': profit,
                   'margen_pct': pct(profit, sales), 'perdidas': sum(r['profit'] < 0 for r in members),
                   'no_rentables': sum(r['profit'] <= 0 for r in members),
                   'pct_perdidas': pct(sum(r['profit'] < 0 for r in members), len(members)),
                   'pct_no_rentables': pct(sum(r['profit'] <= 0 for r in members), len(members)),
                   'desc_prom': sum(r['discount'] for r in members) / len(members),
                   'perdida_bruta': sum(-r['profit'] for r in members if r['profit'] < 0)}
        for label in metrics.keys() & result.keys():
            equal(result[label], metrics[label], 'Descuento ' + label)
    bands = group(rows, band)
    require(len(outputs['13_p06_rangos']) == len(bands), 'Todos los rangos de descuento')
    for result in outputs['13_p06_rangos']:
        check_discount(result, bands[result['banda']])
    subcategories = group(rows, lambda r: (band(r), r['Category'], r['Sub-Category']))
    require(len(outputs['14_p06_subcategorias']) == len(subcategories), 'Todas las subcategorías por rango')
    for result in outputs['14_p06_subcategorias']:
        check_discount(result, subcategories[(result['banda'], result['category'], result['sub_category'])])

    months = group(rows, lambda r: r['date'].replace(day=1))
    start, end = min(months), max(months)
    count = (end.year - start.year) * 12 + end.month - start.month + 1
    require(count <= 120, 'Calendario dentro de los 120 meses soportados')
    calendar = [start.replace(year=start.year + (start.month - 1 + i) // 12,
                              month=(start.month - 1 + i) % 12 + 1) for i in range(count)]
    monthly = [totals(months.get(month, [])) for month in calendar]
    high = sorted(range(count), key=lambda i: (-monthly[i][0], calendar[i]))
    low = sorted(range(count), key=lambda i: (monthly[i][0], calendar[i]))
    require(len(outputs['15_p07_mensual']) == count, 'Calendario mensual completo')
    for index, result in enumerate(outputs['15_p07_mensual']):
        require(result['mes'] == calendar[index].isoformat(), 'Orden y continuidad mensual')
        sales, profit = monthly[index]
        equal(result['ventas'], sales, 'Venta mensual'); equal(result['ganancia'], profit, 'Ganancia mensual')
        for lag, sale_label, profit_label in ((1, 'var_mes_pct', 'var_gan_mes_pct'), (12, 'var_anio_pct', 'var_gan_anio_pct')):
            previous = monthly[index - lag] if index >= lag else None
            equal(result[sale_label], None if previous is None else pct(sales - previous[0], previous[0]), 'Variación mensual/interanual')
            equal(result[profit_label], None if previous is None else pct(profit - previous[1], abs(previous[1])), 'Variación ganancia mensual/interanual')
        equal(result['mm3_ventas'], sum(x[0] for x in monthly[index - 2:index + 1]) / 3 if index >= 2 else None, 'Media móvil ventas')
        equal(result['mm3_ganancia'], sum(x[1] for x in monthly[index - 2:index + 1]) / 3 if index >= 2 else None, 'Media móvil ganancia')
        equal(result['rk_mayor'], high.index(index) + 1, 'Ranking meses mayor')
        equal(result['rk_menor'], low.index(index) + 1, 'Ranking meses menor')
    require({r['mes'] for r in outputs['16_p07_extremos']} == {calendar[i].isoformat() for i in high[:3] + low[:3]}, 'Tres mejores y tres peores meses')

    product_id = group(rows, lambda r: r['Product ID'])
    pareto = {}
    for analysis, metric_index in (('ventas', 0), ('ganancia_neta', 1)):
        values = {key: totals(items)[metric_index] for key, items in product_id.items()}
        ordered = sorted(values, key=lambda k: (-values[k], k))
        total = sum(values.values())
        require(total > 0, 'Denominador Pareto positivo')
        accumulated = Decimal(0); prefix = []
        for identifier in ordered:
            accumulated += values[identifier]; prefix.append(accumulated)
        n80 = next(i + 1 for i, value in enumerate(prefix) if value >= Decimal('.8') * total)
        records = [r for r in outputs['17_p08_pareto'] if r['analisis'] == analysis]
        require(len(records) == len(ordered), 'Todos los productos Pareto')
        for index, result in enumerate(records):
            require(result['product_id'] == ordered[index], 'Orden de contribución Pareto')
            for label, value in {'valor': values[ordered[index]], 'puesto': index + 1, 'total': total,
                                 'acumulado': prefix[index], 'participacion_pct': pct(values[ordered[index]], total),
                                 'acumulado_pct': pct(prefix[index], total), 'n80': n80}.items():
                equal(result[label], value, 'Pareto ' + label)
        summary = next(r for r in outputs['18_p08_resumen'] if r['analisis'] == analysis)
        for label, value in {'productos': len(values), 'total': total, 'productos_80': n80,
                             'pct_productos': pct(n80, len(values)), 'aporte_80': prefix[n80 - 1],
                             'pct_alcanzado': pct(prefix[n80 - 1], total),
                             'productos_negativos': sum(value < 0 for value in values.values())}.items():
            equal(summary[label], value, 'Resumen Pareto ' + label)
        pareto[analysis] = summary

    require(hashlib.sha256(source.read_bytes()).hexdigest() == preparation['source_sha256'], 'Original sin cambios al finalizar')
    result = {'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'checks_passed': checks,
              'source_sha256': preparation['source_sha256'], 'all_questions_3_to_8_match_csv': True,
              'verified_queries': list(outputs), 'regions': outputs['08_p03_regiones'],
              'rfm_reference': reference.isoformat(), 'rfm_customers': len(cm),
              'rfm_segments': outputs['10_p04_segmentos'], 'product_count': len(pm),
              'selected_products': outputs['12_p05_seleccion'], 'discounts': outputs['13_p06_rangos'],
              'top_units': outputs['21_p05_volumen_unidades'],
              'most_affected_subcategories': sorted(outputs['14_p06_subcategorias'], key=lambda r: Decimal(r['perdida_bruta']), reverse=True)[:5],
              'monthly_count': count, 'month_extremes': outputs['16_p07_extremos'], 'pareto': pareto}
    with destination.open('x', encoding='utf-8') as target:
        json.dump(result, target, ensure_ascii=False, indent=2); target.write('\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
