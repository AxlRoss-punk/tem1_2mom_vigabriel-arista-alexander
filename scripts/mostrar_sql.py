#!/usr/bin/env python3
"""Ejecuta un archivo HiveQL del proyecto y muestra la salida real de Beeline."""

import argparse
import subprocess
from pathlib import Path

from cargar_superstore import COMPOSE, ROOT

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--sql', type=Path, required=True)
args = parser.parse_args()
sql_path = (ROOT / args.sql).resolve()
if (ROOT / 'scripts') not in sql_path.parents or sql_path.suffix != '.sql':
    parser.error('El archivo debe ser un SQL dentro de scripts/.')
sql = sql_path.read_bytes()
print('HiveQL: ' + str(sql_path.relative_to(ROOT)), flush=True)
command = ['docker', 'compose', 'exec', '-T', 'hive-server', 'beeline',
           '-u', 'jdbc:hive2://localhost:10000/default', '--silent=true',
           '--showHeader=true', '--outputformat=table', '--force=false',
           '-f', '/dev/stdin']
raise SystemExit(subprocess.run(command, cwd=COMPOSE, input=sql).returncode)
