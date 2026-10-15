"""Execute notebook code cells in fresh processes and record real smoke-test results."""
from pathlib import Path
import argparse
import contextlib
import datetime
import json
import os
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]


def child(path):
    os.environ['MPLBACKEND'] = 'Agg'
    os.environ['COURSE_SMOKE'] = '1'
    os.chdir(ROOT)
    namespace = {'__name__': '__main__'}
    notebook = json.loads(path.read_text(encoding='utf-8'))
    for index, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            print(f'Executing cell {index}', flush=True)
            exec(compile(''.join(cell['source']), f'{path.name}:cell-{index}', 'exec'), namespace)
    print('All code cells completed.', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--child')
    parser.add_argument('--group', choices=['vision','torch-nlp','paddle-nlp','detection','pretrained'])
    parser.add_argument('--resume', action='store_true', help='Skip already-passed notebooks in this group.')
    parser.add_argument('--match', default='', help='Run only paths containing this text.')
    args = parser.parse_args()
    if args.child:
        child(Path(args.child).resolve())
        return
    groups = {
        'vision': sorted((ROOT/'01-image-classification').rglob('*.ipynb')),
        'torch-nlp': sorted((ROOT/'03-sentiment-analysis/pytorch/notebooks').glob('0[1-3]*.ipynb')),
        'paddle-nlp': sorted((ROOT/'03-sentiment-analysis/paddle/notebooks').glob('*.ipynb')),
        'detection': sorted((ROOT/'02-object-detection/notebooks').glob('*.ipynb')),
        'pretrained': sorted((ROOT/'03-sentiment-analysis/pytorch/notebooks').glob('04*.ipynb')),
    }
    if not args.group:
        parser.error('--group is required')
    reports = ROOT/'reports'
    (reports/'logs').mkdir(parents=True, exist_ok=True)
    report_path = reports/f'{args.group}-smoke.json'
    results = json.loads(report_path.read_text(encoding='utf-8'))['results'] if args.resume and report_path.exists() else []
    for path in groups[args.group]:
        relative = path.relative_to(ROOT).as_posix()
        if args.match and args.match not in relative:
            continue
        if args.resume and any(item['notebook']==relative and item['status']=='passed' for item in results):
            continue
        log = reports/'logs'/(args.group+'-'+path.stem+'.log')
        start = time.time()
        env = dict(os.environ, PYTHONIOENCODING='utf-8', MPLBACKEND='Agg', COURSE_SMOKE='1')
        with log.open('w', encoding='utf-8') as handle:
            try:
                run = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child', str(path)],
                                     stdout=handle, stderr=subprocess.STDOUT, env=env, timeout=1200)
                status = 'passed' if run.returncode == 0 else 'failed'
            except subprocess.TimeoutExpired:
                status = 'timed-out'
        result = {'notebook':relative,'status':status,'seconds':round(time.time()-start,2),
                  'log':log.relative_to(ROOT).as_posix()}
        results = [item for item in results if item['notebook'] != relative] + [result]
        print(json.dumps(result),flush=True)
        report_path.write_text(json.dumps({
            'mode':'small-sample smoke execution of all code cells',
            'python':sys.version.split()[0], 'group':args.group,
            'results':results},indent=2)+'\n',encoding='utf-8')
    if any(item['status']!='passed' for item in results):
        raise SystemExit(1)


if __name__=='__main__':
    main()
