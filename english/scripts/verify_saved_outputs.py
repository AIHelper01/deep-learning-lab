"""Check that every delivered notebook has complete, error-free saved execution."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# English course lives in this directory, the mirrored Chinese course one level up.
COURSE_ROOTS = [ROOT, ROOT.parent]
MODULE_DIRS = ['01-image-classification/notebooks',
               '02-object-detection/notebooks',
               '03-sentiment-analysis/pytorch/notebooks',
               '03-sentiment-analysis/paddle/notebooks']
paths = []
for course_root in COURSE_ROOTS:
    for folder in MODULE_DIRS:
        paths.extend(p for p in (course_root / folder).rglob('*.ipynb')
                     if '.ipynb_checkpoints' not in p.parts
                     # The original Chinese PaddleYOLO/YOLO11 lesson is read-only history that
                     # needs the external PaddleYOLO project, so it is never executed.
                     and p.stem != '01-yolo11-rock-paper-scissors')
    archived = course_root / '01-image-classification/archive'
    if archived.is_dir():
        paths.extend(p for p in archived.rglob('*.ipynb')
                     if 'legacy-notebooks' not in p.parts and '.ipynb_checkpoints' not in p.parts)
paths = sorted(set(paths))
rows, problems = [], []
for path in paths:
    nb = json.loads(path.read_text(encoding='utf-8'))
    cells = [c for c in nb['cells'] if c['cell_type'] == 'code' and ''.join(c['source']).strip()]
    outputs = [o for c in cells for o in c.get('outputs', [])]
    relative = Path(os.path.relpath(path, ROOT)).as_posix()
    row = {'notebook': relative, 'code_cells': len(cells),
           'executed_cells': sum(c.get('execution_count') is not None for c in cells),
           'output_items': len(outputs),
           'embedded_images': sum('image/png' in o.get('data', {}) for o in outputs)}
    if row['executed_cells'] != row['code_cells']:
        problems.append(f'Unexecuted cells: {relative}')
    if not outputs or any(o.get('output_type') == 'error' for o in outputs):
        problems.append(f'Missing output or execution error: {relative}')
    if not nb.get('metadata', {}).get('execution_environment', {}).get('completed'):
        problems.append(f'Incomplete execution: {relative}')
    rows.append(row)
report = {'notebooks': len(rows), 'results': rows, 'problems': problems}
(ROOT/'reports/saved-output-checks.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps(report, indent=2))
raise SystemExit(bool(problems))
