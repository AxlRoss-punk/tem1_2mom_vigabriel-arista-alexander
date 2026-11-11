#!/usr/bin/env python3
"""Muestra resultados reales de la carga para la captura de la pregunta 1."""

import argparse
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--completo', action='store_true',
                    help='Mostrar también tipos, productos y códigos postales.')
args = parser.parse_args()
sql = (root / 'scripts/03_verificar_carga.sql').read_text(encoding='utf-8')
if not args.completo:
    # El comentario inicial también contiene un punto y coma: conservarlo
    # y cortar por la siguiente instrucción conocida, no por ese carácter.
    sql = sql.split('\nDESCRIBE ', 1)[0]
print('Pregunta 1: carga en superstore_alexander_2mom', flush=True)
command = ['docker', 'compose', 'exec', '-T', 'hive-server', 'beeline',
           '-u', 'jdbc:hive2://localhost:10000/default', '--silent=true',
           '--showHeader=true', '--outputformat=table', '--force=false',
           '-f', '/dev/stdin']
result = subprocess.run(
    command, input=sql.encode('utf-8'),
    cwd='/home/dante/LI16_Apache_Hive/docker-hadoop-hive-parquet')
raise SystemExit(result.returncode)
