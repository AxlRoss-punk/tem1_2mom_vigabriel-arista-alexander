#!/usr/bin/env python3
"""Ejecuta los bloques analíticos y conserva salidas, hashes y tiempos reales."""

import argparse
import hashlib
import json
import shlex
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from cargar_superstore import ROOT, COMPOSE

GROUPS = {
    'II': ['07_p03_evolucion', '08_p03_regiones', '09_p04_clientes',
           '10_p04_segmentos', '11_p05_productos', '12_p05_seleccion',
           '13_p06_rangos', '14_p06_subcategorias', '21_p05_volumen_unidades'],
    'III': ['15_p07_mensual', '16_p07_extremos', '17_p08_pareto', '18_p08_resumen'],
}


def execute(name):
    sql_path = ROOT / 'scripts' / (name + '.sql')
    sql = sql_path.read_bytes()
    sql_hash = hashlib.sha256(sql).hexdigest()
    output_path = ROOT / 'evidencias' / (name + '.tsv')
    record_path = ROOT / 'evidencias' / (name + '.ejecucion.json')
    if output_path.exists():
        if not record_path.exists():
            raise ValueError('Resultado existente sin procedencia: ' + name)
        previous = json.loads(record_path.read_text(encoding='utf-8'))
        if previous['sql_sha256'] != sql_hash or previous['output_sha256'] != hashlib.sha256(output_path.read_bytes()).hexdigest():
            raise ValueError('El SQL o resultado cambio: ' + name)
        return name, 'ya ejecutado y hashes verificados'
    attempt = 1
    log_path = ROOT / 'evidencias' / (name + '.txt')
    while log_path.exists():
        attempt += 1
        log_path = ROOT / 'evidencias' / (name + f'.intento{attempt}.txt')
    command = ['docker', 'compose', 'exec', '-T', 'hive-server', 'beeline',
               '-u', 'jdbc:hive2://localhost:10000/default', '--silent=true',
               '--showHeader=true', '--outputformat=tsv2', '--force=false',
               '-f', '/dev/stdin']
    started = time.perf_counter()
    process = subprocess.run(command, cwd=COMPOSE, input=sql, capture_output=True)
    elapsed = time.perf_counter() - started
    with log_path.open('x', encoding='utf-8') as log:
        log.write('$ ' + shlex.join(command) + '\nSQL: ' + sql_path.name + '\n')
        log.write('SQL SHA-256: ' + sql_hash + '\n')
        log.write(process.stdout.decode('utf-8', errors='replace'))
        log.write(process.stderr.decode('utf-8', errors='replace'))
        log.write(f'\n[exit_code={process.returncode}; elapsed_seconds={elapsed:.6f}]\n')
    if process.returncode:
        raise RuntimeError('Hive rechazo ' + name + '; consultar ' + str(log_path))
    with output_path.open('xb') as target:
        target.write(process.stdout)
    record = {
        'executed_at_utc': datetime.now(timezone.utc).isoformat(),
        'sql_file': str(sql_path.relative_to(ROOT)), 'sql_sha256': sql_hash,
        'output_file': str(output_path.relative_to(ROOT)),
        'output_sha256': hashlib.sha256(process.stdout).hexdigest(),
        'exit_code': process.returncode, 'elapsed_seconds': elapsed,
        'log_file': str(log_path.relative_to(ROOT)),
        'database': 'superstore_alexander_2mom', 'database_modified': False,
    }
    with record_path.open('x', encoding='utf-8') as target:
        json.dump(record, target, ensure_ascii=False, indent=2)
        target.write('\n')
    return name, f'ejecutado: {elapsed:.2f} s'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bloque', choices=['II', 'III', 'todos'], default='todos')
    args = parser.parse_args()
    names = GROUPS['II'] + GROUPS['III'] if args.bloque == 'todos' else GROUPS[args.bloque]
    failures = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        pending = {pool.submit(execute, name): name for name in names}
        for future in as_completed(pending):
            try:
                print(' | '.join(future.result()), flush=True)
            except Exception as error:
                failures.append(str(error))
                print('ERROR: ' + str(error), flush=True)
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
