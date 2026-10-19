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
    parser.add_argument('--language', choices=['en', 'zh-CN'], default='en')
    parser.add_argument('--notebook', action='append',
                        help='Only execute notebooks whose filename matches this stem. Repeatable.')
    parser.add_argument('--cwd', choices=['root', 'notebook'], default='root',
                        help='Kernel working directory. Course notebooks resolve data from the course root; '
                             'the vision archive notebook resolves "../data", "../outputs" and its own '
                             '"assets/" from the notebook directory, so it needs --cwd notebook.')
    args = parser.parse_args()
    # 中文课程镜像位于仓库根目录的模块树，英文课程在 english/ 下。
    base = ROOT if args.language == 'en' else ROOT.parent
    groups = {
        'vision': sorted([*(base/'01-image-classification/notebooks').rglob('*.ipynb'),
                          *(base/'01-image-classification/archive').rglob('*.ipynb')]),
        'pytorch': sorted((base/'03-sentiment-analysis/pytorch/notebooks').glob('*.ipynb')),
        'paddle': sorted((base/'03-sentiment-analysis/paddle/notebooks').glob('*.ipynb')),
        'detection': sorted((base/'02-object-detection/notebooks').glob('*.ipynb')),
    }
    # archive/legacy-notebooks is read-only course history: it is never re-executed.
    # The original Chinese PaddleYOLO/YOLO11 lesson lives in notebooks/ again by request,
    # but it still depends on that external project, so it stays out of every execution run.
    groups = {key: [p for p in paths
                    if '.ipynb_checkpoints' not in p.parts and 'legacy-notebooks' not in p.parts
                    and p.stem != '01-yolo11-rock-paper-scissors']
              for key, paths in groups.items()}
    reports = ROOT/'reports'
    suffix = '' if args.language == 'en' else '-zh-CN'
    report_file = reports/f'{args.group}{suffix}-executed.json'
    # Reports accumulate: a targeted --notebook run must not drop the rows of other notebooks.
    results = []
    report_extra = {}
    if report_file.exists():
        try:
            previous = json.loads(report_file.read_text(encoding='utf-8'))
            results = previous.get('results', [])
            report_extra = {key: value for key, value in previous.items()
                            if key not in {'group', 'language', 'python', 'executable', 'results'}}
        except (json.JSONDecodeError, OSError):
            results = []
    os.environ['COURSE_SMOKE'] = '0'
    epochs_override = os.environ.get('COURSE_EPOCHS')
    run_mode = (f'{epochs_override}-epoch pipeline check via COURSE_EPOCHS'
                if epochs_override else 'Default classroom training parameters')
    run_mode_label = (('通过 COURSE_EPOCHS 指定的 ' + str(epochs_override) + ' 轮流程检查'
                       if epochs_override else '课堂默认训练参数')
                      if args.language == 'zh-CN' else run_mode)
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['OMP_NUM_THREADS'] = '2'
    os.environ['MKL_NUM_THREADS'] = '2'
    # Matplotlib inline produces display_data PNGs in the saved notebook.
    os.environ.pop('MPLBACKEND', None)
    if args.notebook:
        groups[args.group] = [path for path in groups[args.group]
                              if path.stem in set(args.notebook)]
        if not groups[args.group]:
            parser.error(f'No notebook matched {args.notebook} in group {args.group}.')
    for path in groups[args.group]:
        relative = Path(os.path.relpath(path, ROOT)).as_posix()
        if args.resume and any(row['notebook']==relative and row['status']=='passed'
                               and row.get('run_mode')==run_mode for row in results):
            continue
        print(f'Executing and saving: {relative}', flush=True)
        nb = nbformat.read(path, as_version=4)
        nb.cells = [cell for cell in nb.cells if 'course-runtime-info' not in cell.get('metadata', {}).get('tags', [])]
        package = 'paddlepaddle' if args.group=='paddle' else 'torch'
        expected = '3.3.1' if args.group=='paddle' else '2.14.1'
        if args.language == 'zh-CN':
            runtime_source = (
                'import sys\nfrom importlib.metadata import version\n'
                'from IPython import get_ipython\n'
                'get_ipython().run_line_magic("matplotlib", "inline")\n'
                'assert sys.version_info[:2] == (3, 12), "请选择项目的 Python 3.12 内核。"\n'
                f'assert version({package!r}).split("+")[0] == {expected!r}, "请选择项目锁定的运行环境。"\n'
                'print("Python：", sys.version.split()[0])\n'
                f'print({package!r} + "：", version({package!r}))\n'
                f'print("运行模式：", {run_mode_label!r})')
        else:
            runtime_source = (
                'import sys\nfrom importlib.metadata import version\n'
                'from IPython import get_ipython\n'
                'get_ipython().run_line_magic("matplotlib", "inline")\n'
                'assert sys.version_info[:2] == (3, 12), "Select the Python 3.12 project kernel."\n'
                f'assert version({package!r}).split("+")[0] == {expected!r}, "Select the locked project environment."\n'
                'print("Python:", sys.version.split()[0])\n'
                f'print({package!r} + ":", version({package!r}))\n'
                f'print("Run mode:", {run_mode!r})')
        runtime = nbformat.v4.new_code_cell(
            runtime_source, metadata={'tags':['course-runtime-info']})
        nb.cells.insert(1, runtime)
        for cell in nb.cells:
            if cell.cell_type=='code':
                cell.outputs = []
                cell.execution_count = None
        nb.metadata['execution_environment'] = {
            'python':sys.version.split()[0], 'executable':sys.executable,
            'mode': (f'{epochs_override}-epoch pipeline check' if epochs_override else 'default classroom parameters'),
            'language': args.language,
            'manager':'uv', 'completed':False}
        start = time.time()
        error = None
        try:
            def cell_saved(cell, cell_index, **kwargs):
                nbformat.write(nb, path)
                print(f'  Saved cell {cell_index}: {path.name}', flush=True)

            client = NotebookClient(nb, timeout=5400, kernel_name='python3',
                                    resources={'metadata': {'path': str(path.parent if args.cwd == 'notebook' else base)}},
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
        row = {'notebook':relative,'status':status,'run_mode':run_mode,'seconds':round(time.time()-start,2),
               'code_cells':sum(c.cell_type=='code' for c in nb.cells),
               'output_items':sum(len(c.get('outputs',[])) for c in nb.cells),
               'png_outputs':sum('image/png' in out.get('data',{}) for c in nb.cells for out in c.get('outputs',[]))}
        if error:
            row['error'] = error
        results = sorted([item for item in results if item['notebook']!=relative] + [row],
                         key=lambda item: item['notebook'])
        report = {'group':args.group,'language':args.language,'python':sys.version.split()[0],
                  'executable':sys.executable}
        report.update({key: value for key, value in report_extra.items() if key not in report})
        report['results'] = results
        report_file.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(row),flush=True)
    if any(row['status']!='passed' for row in results):
        raise SystemExit(1)


if __name__=='__main__':
    main()
