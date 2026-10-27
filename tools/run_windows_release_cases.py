#!/usr/bin/env python3
"""Run staged, identical WEPP cases on native Windows or Linux.

The case manifest lists directories with runs/ and output/ plus ordered run cards.
Each card names the watershed or hillslope executable explicitly. Outputs must be
fresh: reuse of a nonempty output directory is rejected.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--watershed', type=Path, required=True)
    parser.add_argument('--hill', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args()
    root = args.root.resolve()
    binaries = {'watershed': args.watershed.resolve(), 'hill': args.hill.resolve()}
    cases = json.loads((root/'cases.json').read_text())
    results = []
    for case in cases:
        directory = root/case['name']
        output = directory/'output'
        output.mkdir(exist_ok=True)
        if any(output.iterdir()):
            raise RuntimeError(f'Output directory is not empty: {output}')
        for card in case['cards']:
            role = card['role']
            with (directory/'runs'/card['file']).open('rb') as stream:
                process = subprocess.run([str(binaries[role])], stdin=stream,
                    cwd=directory/'runs', capture_output=True, timeout=args.timeout,
                    env={**os.environ, 'LC_ALL': 'C', 'TZ': 'UTC'})
            stdout = process.stdout.decode(errors='replace')
            stderr = process.stderr.decode(errors='replace')
            stem = Path(card['file']).stem
            (directory/f'{stem}.stdout.log').write_text(stdout)
            (directory/f'{stem}.stderr.log').write_text(stderr)
            marker = 'WEPP COMPLETED ' + ('HILLSLOPE' if role == 'hill' else 'WATERSHED') + ' SIMULATION SUCCESSFULLY'
            passed = process.returncode == 0 and marker in stdout and not re.search(
                r'Fortran runtime error|Program stop|Bad value during floating point read', stdout+stderr, re.I)
            results.append({'case': case['name'], 'card': card['file'], 'role': role,
                            'returncode': process.returncode, 'passed': passed})
            print(json.dumps(results[-1]), flush=True)
            if not passed:
                break
    (root/'execution.json').write_text(json.dumps(results, indent=2)+'\n')
    expected = sum(len(case['cards']) for case in cases)
    return 0 if len(results) == expected and all(r['passed'] for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
