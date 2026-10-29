"""Run member suites in isolated pytest processes and retain every exit status."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SUITES = ['f01_f03', 'f04_f06', 'f07_f09', 'f10_f12']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=SUITES, help='Run just one member suite')
    parser.add_argument('--collect-only', action='store_true', help='Check collection without opening Chrome')
    args = parser.parse_args()
    output = ROOT / 'artifacts'
    output.mkdir(exist_ok=True)
    results = {}
    for suite in [args.suite] if args.suite else SUITES:
        command = [sys.executable, '-m', 'pytest', '-c', 'pytest.ini', '--junitxml=' + str(output / (suite + '.xml'))]
        command += ['tests'] if suite in ['f07_f09', 'f10_f12'] else ['.']
        if args.collect_only:
            command.append('--collect-only')
        print('\nRunning ' + suite, flush=True)
        results[suite] = subprocess.run(command, cwd=ROOT/'suites'/suite).returncode
    (output/'summary.json').write_text(json.dumps({'collection_only': args.collect_only, 'exit_codes': results}, indent=2), encoding='utf-8')
    return 0 if all(code == 0 for code in results.values()) else 1

if __name__ == '__main__':
    sys.exit(main())
