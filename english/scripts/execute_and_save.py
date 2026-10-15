"""Execute course notebooks through a real Jupyter kernel and save visible outputs."""
from pathlib import Path
import argparse
import datetime
import json
import os
import sys
import time

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--group', required=True,
                        choices=['vision','pytorch','paddle','detection'])
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    groups = {
        'vision': sorted([*(ROOT/'01-image-classification/notebooks').rglob('*.ipynb'),
                          *(ROOT/'01-image-classification/archive').rglob('*.ipynb')]),
        'pytorch': sorted((ROOT/'03-sentiment-analysis/pytorch/notebooks').glob('*.ipynb')),
        'paddle': sorted((ROOT/'03-sentiment-analysis/paddle/notebooks').glob('*.ipynb')),
        'detection': sorted((ROOT/'02-object-detection/notebooks').glob('*.ipynb')),
    }
    reports = ROOT/'reports'
    report_file = reports/f'{args.group}-executed.json'
    results = json.loads(report_file.read_text(encoding='utf-8'))['results'] if args.resume and report_file.exists() else []
    os.environ['COURSE_SMOKE'] = '0'
    epochs_override = os.environ.get('COURSE_EPOCHS')
    run_mode = (f'{epochs_override}-epoch pipeline check via COURSE_EPOCHS'
                if epochs_override else 'Default classroom training parameters')
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['OMP_NUM_THREADS'] = '2'
    os.environ['MKL_NUM_THREADS'] = '2'
    # Matplotlib inline produces display_data PNGs in the saved notebook.
    os.environ.pop('MPLBACKEND', None)
    for path in groups[args.group]:
        relative = path.relative_to(ROOT).as_posix()
        if args.resume and any(row['notebook']==relative and row['status']=='passed' for row in results):
            continue
        print(f'Executing and saving: {relative}', flush=True)
        nb = nbformat.read(path, as_version=4)
        nb.cells = [cell for cell in nb.cells if 'course-runtime-info' not in cell.get('metadata', {}).get('tags', [])]
        package = 'paddlepaddle' if args.group=='paddle' else 'torch'
        expected = '3.3.1' if args.group=='paddle' else '2.14.1'
        runtime = nbformat.v4.new_code_cell(
            'import sys\nfrom importlib.metadata import version\n'
            'from IPython import get_ipython\n'
            'get_ipython().run_line_magic("matplotlib", "inline")\n'
            'assert sys.version_info[:2] == (3, 12), "Select the Python 3.12 project kernel."\n'
            f'assert version({package!r}).split("+")[0] == {expected!r}, "Select the locked project environment."\n'
            'print("Python:", sys.version.split()[0])\n'
            f'print({package!r} + ":", version({package!r}))\n'
            f'print("Run mode:", {run_mode!r})',
            metadata={'tags':['course-runtime-info']})
        nb.cells.insert(1, runtime)
        for cell in nb.cells:
            if cell.cell_type=='code':
                cell.outputs = []
                cell.execution_count = None
        nb.metadata['execution_environment'] = {
            'python':sys.version.split()[0], 'executable':sys.executable,
            'mode': (f'{epochs_override}-epoch pipeline check' if epochs_override else 'default classroom parameters'),
            'manager':'uv', 'completed':False}
        start = time.time()
        error = None
        try:
            def cell_saved(cell, cell_index, **kwargs):
                nbformat.write(nb, path)
                print(f'  Saved cell {cell_index}: {path.name}', flush=True)

            client = NotebookClient(nb, timeout=5400, kernel_name='python3',
                                    resources={'metadata':{'path':str(ROOT)}},
                                    allow_errors=False, record_timing=True,
                                    on_cell_executed=cell_saved)
            client.execute()
            status = 'passed'
            nb.metadata.execution_environment.completed = True
        except Exception as exc:
            status = 'failed'
            error = f'{type(exc).__name__}: {str(exc)[-3000:]}'
        finally:
            nbformat.write(nb, path)
        row = {'notebook':relative,'status':status,'seconds':round(time.time()-start,2),
               'code_cells':sum(c.cell_type=='code' for c in nb.cells),
               'output_items':sum(len(c.get('outputs',[])) for c in nb.cells),
               'png_outputs':sum('image/png' in out.get('data',{}) for c in nb.cells for out in c.get('outputs',[]))}
        if error:
            row['error'] = error
        results = [item for item in results if item['notebook']!=relative] + [row]
        report_file.write_text(json.dumps({'group':args.group,'python':sys.version.split()[0],
                                           'executable':sys.executable,'results':results},indent=2)+'\n',encoding='utf-8')
        print(json.dumps(row),flush=True)
    if any(row['status']!='passed' for row in results):
        raise SystemExit(1)


if __name__=='__main__':
    main()
