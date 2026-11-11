#!/usr/bin/env python3
"""Compara CSV y ORC con calentamiento, orden alternado y resultados iguales."""

import csv
import hashlib
import io
import json
import shlex
import statistics
import subprocess
import time
from datetime import datetime, timezone
from decimal import Decimal

from cargar_superstore import ROOT, COMPOSE


def rows(data):
    reader = csv.DictReader(io.StringIO(data.decode('utf-8')), delimiter='\t', quoting=csv.QUOTE_NONE)
    result = []
    for item in reader:
        item = {key.rsplit('.', 1)[-1]: value for key, value in item.items()}
        result.append((item['region'], int(item['anio']), Decimal(item['ventas']), Decimal(item['ganancia'])))
    return sorted(result)


def main():
    report = ROOT / 'evidencias/optimizacion_mediciones.json'
    log_path = ROOT / 'evidencias/optimizacion_ejecucion.txt'
    plan_paths = {name: ROOT / f'evidencias/optimizacion_plan_{name}.txt' for name in ('csv', 'orc')}
    for path in [report, log_path, *plan_paths.values()]:
        if path.exists():
            raise FileExistsError('Se conserva el registro existente: ' + str(path))
    expected = rows((ROOT / 'evidencias/07_p03_evolucion.tsv').read_bytes())
    sql = {name: (ROOT / 'scripts' / filename).read_bytes() for name, filename in
           (('csv', '19_optimizar_csv.sql'), ('orc', '20_optimizar_orc.sql'))}
    measurements = []
    with log_path.open('x', encoding='utf-8') as log:
        def execute(arguments, input_bytes=None):
            command = ['docker', 'compose', 'exec', '-T', 'hive-server', *arguments]
            started = time.perf_counter()
            process = subprocess.run(command, cwd=COMPOSE, input=input_bytes, capture_output=True)
            elapsed = time.perf_counter() - started
            log.write('$ ' + shlex.join(command) + '\n')
            log.write(process.stdout.decode('utf-8', errors='replace'))
            log.write(process.stderr.decode('utf-8', errors='replace'))
            log.write(f'\n[exit_code={process.returncode}; elapsed_seconds={elapsed:.6f}]\n\n')
            log.flush()
            if process.returncode:
                raise RuntimeError('Falló la medición; consultar optimizacion_ejecucion.txt.')
            return process.stdout, elapsed
        base = ['beeline', '-u', 'jdbc:hive2://localhost:10000/default', '--silent=true',
                '--showHeader=true', '--outputformat=tsv2', '--force=false', '-f', '/dev/stdin']
        schedule = [('csv', True), ('orc', True), ('csv', False), ('orc', False), ('orc', False), ('csv', False)]
        for name, warmup in schedule:
            output, elapsed = execute(base, sql[name])
            if rows(output) != expected:
                raise AssertionError('CSV y ORC no coinciden con los resultados regionales.')
            measurements.append({'storage': name, 'warmup': warmup, 'wall_seconds': elapsed,
                                 'rows': len(expected), 'results_match': True})
            print(f'{name}: {elapsed:.3f} s; calentamiento={warmup}; resultado verificado', flush=True)
        for name in ('csv', 'orc'):
            # Los dos SET iniciales quedan antes de EXPLAIN; solo se explica el SELECT.
            query = sql[name].decode('utf-8').split(';', 2)[2].strip()
            explain = b'SET hive.local.time.zone=UTC; SET hive.datetime.formatter=SIMPLE;\nEXPLAIN ' + query.encode('utf-8')
            output, _ = execute(base, explain)
            with plan_paths[name].open('xb') as target:
                target.write(output)
        describe, _ = execute(base, b'DESCRIBE FORMATTED superstore_alexander_2mom.superstore;')
        location = None
        for line in describe.decode('utf-8').splitlines():
            cells = [cell.strip() for cell in line.split('\t')]
            if cells and cells[0].rstrip(':').lower() == 'location':
                location = cells[1]
        if not location:
            raise ValueError('No se pudo identificar la ruta de la tabla ORC.')
        sizes = {}
        for name, path in (('csv', 'hdfs://namenode:8020/user/dante/superstore_alexander_2mom/ingesta'), ('orc', location)):
            output, _ = execute(['hdfs', 'dfs', '-du', '-s', path])
            sizes[name] = int(output.decode('utf-8').split()[0])
    medians = {name: statistics.median(m['wall_seconds'] for m in measurements if m['storage'] == name and not m['warmup']) for name in ('csv', 'orc')}
    result = {'measured_at_utc': datetime.now(timezone.utc).isoformat(), 'measurements': measurements,
              'median_wall_seconds': medians, 'logical_hdfs_bytes': sizes,
              'space_reduction_pct': 100 * (1 - sizes['orc'] / sizes['csv']),
              'sql_sha256': {name: hashlib.sha256(value).hexdigest() for name, value in sql.items()},
              'all_results_equal': True, 'data_modified': False,
              'timing_scope': 'Tiempo de pared: cliente Docker/Beeline, conexion y consulta; dos repeticiones medidas por formato, después de un calentamiento. Sin consultas simultaneas de este ejecutor.',
              'limitations': 'Dataset pequeno; cache y arranque del cliente influyen. Las mediciones no demuestran una ventaja universal.'}
    with report.open('x', encoding='utf-8') as target:
        json.dump(result, target, ensure_ascii=False, indent=2); target.write('\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
