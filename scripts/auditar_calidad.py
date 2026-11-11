#!/usr/bin/env python3
"""Ejecuta la auditoría de solo lectura y contrasta sus métricas con el CSV."""

import argparse
import csv
import hashlib
import io
import json
import shlex
import subprocess
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

from cargar_superstore import COLUMNS, COMPOSE, DB, ROOT


def parse_date(value):
    try:
        return datetime.strptime(value.strip(), '%m/%d/%Y').date()
    except (ValueError, AttributeError):
        return None


def invalid_date(value):
    parsed = parse_date(value)
    return parsed is None or f'{parsed.month}/{parsed.day}/{parsed.year:04}' != value.strip()


def number(value, converter):
    try:
        return converter(value)
    except (ValueError, TypeError, InvalidOperation):
        return None


def expected_metrics(rows):
    typed = []
    for row in rows:
        values = list(row)
        for index in (0, 18):
            values[index] = number(values[index], int)
        for index in (17, 19, 20):
            values[index] = number(values[index], Decimal)
        for index in (2, 3):
            values[index] = parse_date(values[index])
        typed.append(values)
    ids = Counter(row[0] for row in typed if row[0] is not None)
    metrics = {
        'registros_analiticos': len(typed),
        'registros_origen': len(rows),
        'identificadores_fila_duplicados': sum(count > 1 for count in ids.values()),
        'filas_duplicadas_adicionales': sum(count - 1 for count in ids.values()),
        'ordenes_unicas': len({row[1] for row in typed if row[1] is not None}),
        'clientes_unicos': len({row[5] for row in typed if row[5] is not None}),
        'filas_con_algun_null': sum(any(value is None for value in row) for row in typed),
        'valores_null_21_columnas': sum(value is None for row in typed for value in row),
        'pedidos_fecha_invalida_origen': sum(invalid_date(row[2]) for row in rows),
        'envios_fecha_invalida_origen': sum(invalid_date(row[3]) for row in rows),
        'filas_fecha_invalida_origen': sum(invalid_date(row[2]) or invalid_date(row[3]) for row in rows),
        'filas_fecha_null_analitica': sum(row[2] is None or row[3] is None for row in typed),
        'ventas_cero_o_negativas': sum(row[17] is not None and row[17] <= 0 for row in typed),
        'descuentos_fuera_0_1': sum(row[19] is not None and not 0 <= row[19] <= 1 for row in typed),
        'envios_anteriores_al_pedido': sum(row[2] is not None and row[3] is not None and row[3] < row[2] for row in typed),
        'cantidades_no_positivas': sum(row[18] is not None and row[18] <= 0 for row in typed),
        'postales_cuatro_digitos': sum(len(row[11]) == 4 and row[11].isdigit() for row in rows),
        'postales_con_cero_inicial': sum(row[11].startswith('0') and row[11].isdigit() for row in rows),
        'productos_con_espacios_ascii_extremos': sum(row[16] != row[16].strip(' ') for row in rows),
        'productos_con_espacio_no_separable': sum('\u00a0' in row[16] for row in rows),
    }
    nulls = {column: sum(row[index] is None for row in typed)
             for index, column in enumerate(COLUMNS)}
    return metrics, nulls


def command_for(script, output_format='tsv2'):
    return ['docker', 'compose', 'exec', '-T', 'hive-server', 'beeline',
            '-u', 'jdbc:hive2://localhost:10000/default', '--silent=true',
            '--showHeader=true', f'--outputformat={output_format}', '--force=false',
            '-f', '/dev/stdin'], (ROOT / 'scripts' / script).read_bytes()


def table_dict(output, expected_header):
    lines = output.decode('utf-8').strip().splitlines()
    if not lines or lines[0].split('\t') != expected_header:
        raise ValueError('La salida de Hive no tiene las columnas esperadas.')
    result = {}
    for expected_order, line in enumerate(lines[1:], 1):
        order, key, value = line.split('\t')
        if int(order) != expected_order:
            raise ValueError('El orden de los indicadores devueltos no coincide.')
        if key in result:
            raise ValueError('La salida de Hive contiene indicadores repetidos.')
        result[key] = int(value)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mostrar', action='store_true',
                        help='Consultar el resumen en tabla para una captura, sin escribir archivos.')
    args = parser.parse_args()
    if args.mostrar:
        command, sql = command_for('04_p02_resumen.sql', 'table')
        print('Pregunta 2: auditoría de superstore_alexander_2mom', flush=True)
        raise SystemExit(subprocess.run(command, cwd=COMPOSE, input=sql).returncode)

    artifacts = {name: ROOT / 'evidencias' / name for name in (
        'p02_resumen.tsv', 'p02_nulls.tsv', 'p02_incidencias.tsv',
        'p02_ejecucion.txt', 'p02_verificacion.json')}
    for path in artifacts.values():
        if path.exists():
            raise FileExistsError(f'Se rechaza sobrescribir un registro existente: {path}')
    preparation = json.loads((ROOT / 'evidencias/preparacion_ingesta.json').read_text(encoding='utf-8'))
    source = Path(preparation['source'])
    source_bytes = source.read_bytes()
    original_hash = hashlib.sha256(source_bytes).hexdigest()
    if original_hash != preparation['source_sha256']:
        raise ValueError('El original difiere del hash de referencia.')
    all_rows = list(csv.reader(io.StringIO(source_bytes.decode('cp1252'), newline=''), strict=True))
    if len(all_rows[0]) != 21 or any(len(row) != 21 for row in all_rows[1:]):
        raise ValueError('El CSV original no conserva la estructura de 21 columnas.')
    expected, expected_nulls = expected_metrics(all_rows[1:])

    outputs = {}
    with artifacts['p02_ejecucion.txt'].open('x', encoding='utf-8') as log:
        for sql_name, output_name in (
            ('04_p02_resumen.sql', 'p02_resumen.tsv'),
            ('05_p02_nulls.sql', 'p02_nulls.tsv'),
            ('06_p02_incidencias.sql', 'p02_incidencias.tsv'),
        ):
            command, sql = command_for(sql_name)
            process = subprocess.run(command, cwd=COMPOSE, input=sql, capture_output=True)
            log.write('$ ' + shlex.join(command) + '\nSQL: ' + sql_name + '\n')
            log.write('SQL SHA-256: ' + hashlib.sha256(sql).hexdigest() + '\n')
            log.write(process.stdout.decode('utf-8', errors='replace'))
            log.write(process.stderr.decode('utf-8', errors='replace'))
            log.write(f'\n[exit_code={process.returncode}]\n\n')
            log.flush()
            if process.returncode != 0:
                raise RuntimeError('Falló Hive; consultar el registro de ejecución.')
            outputs[output_name] = process.stdout

    actual = table_dict(outputs['p02_resumen.tsv'], ['orden', 'indicador', 'valor'])
    nulls = table_dict(outputs['p02_nulls.tsv'], ['orden', 'columna', 'cantidad_null'])
    if actual != expected or nulls != expected_nulls:
        raise ValueError('Las métricas Hive no coinciden con la comprobación independiente del CSV.')
    if hashlib.sha256(source.read_bytes()).hexdigest() != original_hash:
        raise ValueError('El hash del CSV original cambió.')
    for name, output in outputs.items():
        with artifacts[name].open('xb') as destination:
            destination.write(output)
    report = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'database': DB,
        'hive_metrics': actual,
        'nulls_by_column': nulls,
        'independent_csv_metrics_match': actual == expected,
        'independent_csv_nulls_match': nulls == expected_nulls,
        'source_sha256': original_hash,
        'source_unchanged': True,
        'database_operations': 'SELECT y opciones de sesión; sin DDL ni DML',
        'screenshot_status': 'pendiente de captura del estudiante',
    }
    with artifacts['p02_verificacion.json'].open('x', encoding='utf-8') as destination:
        json.dump(report, destination, ensure_ascii=False, indent=2)
        destination.write('\n')
    print(outputs['p02_resumen.tsv'].decode('utf-8'))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
