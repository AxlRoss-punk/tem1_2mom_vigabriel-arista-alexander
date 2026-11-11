#!/usr/bin/env python3
"""Ejecuta la pregunta 1 en un espacio nuevo y compara todos los valores."""

import csv
import hashlib
import io
import json
import re
import shlex
import subprocess
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = Path('/home/dante/LI16_Apache_Hive/docker-hadoop-hive-parquet')
DB = 'superstore_alexander_2mom'
HDFS_ROOT = f'hdfs://namenode:8020/user/dante/{DB}'
COLUMNS = [
    'row_id', 'order_id', 'order_date', 'ship_date', 'ship_mode',
    'customer_id', 'customer_name', 'segment', 'country', 'city', 'state',
    'postal_code', 'region', 'product_id', 'category', 'sub_category',
    'product_name', 'sales', 'quantity', 'discount', 'profit',
]


def convert(row, source=False):
    values = list(row)
    for index in (0, 18):
        values[index] = int(values[index])
    for index in (17, 19, 20):
        values[index] = Decimal(values[index])
    for index in (2, 3):
        if source:
            values[index] = datetime.strptime(values[index], '%m/%d/%Y').date()
        else:
            values[index] = datetime.strptime(values[index], '%Y-%m-%d').date()
    return values


def main():
    report_path = ROOT / 'evidencias/p01_verificacion.json'
    log_path = ROOT / 'evidencias/p01_ejecucion.txt'
    checks_path = ROOT / 'evidencias/p01_comprobaciones.tsv'
    for path in (report_path, log_path, checks_path):
        if path.exists():
            raise FileExistsError(f'Se rechaza sobrescribir: {path}')
    preparation = json.loads((ROOT / 'evidencias/preparacion_ingesta.json').read_text())
    prepared = ROOT / preparation['output']
    prepared_bytes = prepared.read_bytes()
    if hashlib.sha256(prepared_bytes).hexdigest() != preparation['output_sha256']:
        raise ValueError('La copia preparada cambió respecto al registro.')
    source_rows = list(csv.reader(io.StringIO(prepared_bytes.decode('utf-8'), newline=''), strict=True))[1:]
    if any('\t' in field or '\n' in field or '\r' in field
           for row in source_rows for field in row):
        raise ValueError('La verificación TSV requiere campos sin tabulaciones ni saltos.')
    expected = sorted((convert(row, source=True) for row in source_rows), key=lambda row: row[0])
    if not COMPOSE.is_dir():
        raise FileNotFoundError(COMPOSE)

    with log_path.open('x', encoding='utf-8') as log:
        def execute(arguments, input_bytes=None, accepted=(0,), binary=False):
            command = ['docker', 'compose', 'exec', '-T', 'hive-server', *arguments]
            log.write('$ ' + shlex.join(command) + '\n')
            log.flush()
            process = subprocess.run(command, cwd=COMPOSE, input=input_bytes,
                                     capture_output=True)
            if binary:
                log.write('[Salida de datos conservada solo en memoria]\n')
            else:
                log.write(process.stdout.decode('utf-8', errors='replace'))
            log.write(process.stderr.decode('utf-8', errors='replace'))
            log.write(f'\n[exit_code={process.returncode}]\n')
            log.flush()
            if process.returncode not in accepted:
                raise RuntimeError(f'Falló un comando; consultar {log_path}')
            return process

        def hive(query=None, script=None, binary=False):
            base = ['beeline', '-u', 'jdbc:hive2://localhost:10000/default',
                    '--silent=true', '--showHeader=true', '--outputformat=tsv2',
                    '--force=false']
            if script is not None:
                sql = (ROOT / script).read_bytes()
                if re.search(rb'\b(DROP|TRUNCATE)\b|INSERT\s+OVERWRITE|\b(?:db_alexander|dbec_alexander|db3_alexander|db4_alexander)\b', sql, re.I):
                    raise ValueError('El SQL contiene una operación fuera del alcance autorizado.')
                return execute(base + ['-f', '/dev/stdin'], sql, binary=binary)
            return execute(base + ['-e', query], binary=binary)

        databases = hive(query=f"SHOW DATABASES LIKE '{DB}';").stdout.decode('utf-8')
        if DB in [line.strip() for line in databases.splitlines()]:
            raise RuntimeError('La base ya existe; no se reutilizará ni se repetirá la carga.')
        exists = execute(['hdfs', 'dfs', '-test', '-e', HDFS_ROOT], accepted=(0, 1))
        if exists.returncode == 0:
            raise RuntimeError('La ruta de HDFS ya existe; no se sobrescribirá.')
        execute(['hdfs', 'dfs', '-mkdir', '-p', HDFS_ROOT + '/ingesta'])
        hdfs_file = HDFS_ROOT + '/ingesta/superstore_utf8.csv'
        execute(['hdfs', 'dfs', '-put', '-', hdfs_file], prepared_bytes)
        uploaded = execute(['hdfs', 'dfs', '-cat', hdfs_file], binary=True).stdout
        hdfs_hash = hashlib.sha256(uploaded).hexdigest()
        if hdfs_hash != preparation['output_sha256']:
            raise ValueError('El archivo en HDFS no coincide con la copia preparada.')
        log.write('SHA-256 HDFS verificado: ' + hdfs_hash + '\n')

        hive(script='scripts/01_modelo.sql')
        hive(script='scripts/02_carga.sql')
        raw_count_text = hive(query=f'SELECT COUNT(*) AS registros FROM {DB}.superstore_raw;').stdout.decode('utf-8')
        raw_count = int(raw_count_text.strip().splitlines()[-1])
        export = hive(query=f"SELECT {', '.join(COLUMNS)} FROM {DB}.superstore ORDER BY row_id;", binary=True)
        lines = export.stdout.decode('utf-8').splitlines()
        headers = [column.split('.')[-1] for column in lines[0].split('\t')]
        if headers != COLUMNS:
            raise ValueError('Las columnas devueltas por Hive no coinciden con el modelo.')
        actual = []
        for position, line in enumerate(lines[1:], 1):
            values = line.split('\t')
            if len(values) != 21:
                raise ValueError(f'El registro Hive {position} no contiene 21 campos.')
            actual.append(convert(values))
        if raw_count != 9994 or len(actual) != 9994 or actual != expected:
            raise ValueError('Los registros de Hive no coinciden con los del CSV preparado.')

        checks = hive(script='scripts/03_verificar_carga.sql').stdout.decode('utf-8')
        with checks_path.open('x', encoding='utf-8', newline='\n') as target:
            target.write(checks)
        original_hash = hashlib.sha256(Path(preparation['source']).read_bytes()).hexdigest()
        if original_hash != preparation['source_sha256']:
            raise ValueError('Cambió el CSV original.')
        result = {
            'generated_at_utc': datetime.now(timezone.utc).isoformat(),
            'database': DB,
            'raw_records': raw_count,
            'analytical_records': len(actual),
            'columns_compared': 21,
            'field_values_compared': len(actual) * 21,
            'all_values_match_expected_types': actual == expected,
            'utf8_hdfs_sha256': hdfs_hash,
            'original_sha256': original_hash,
            'original_unchanged': True,
            'screenshot_status': 'pendiente de captura del estudiante',
            'console_log': str(log_path.relative_to(ROOT)),
            'checks_output': str(checks_path.relative_to(ROOT)),
        }
        with report_path.open('x', encoding='utf-8', newline='\n') as target:
            json.dump(result, target, ensure_ascii=False, indent=2)
            target.write('\n')
        print(checks)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
