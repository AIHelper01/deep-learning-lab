"""Static checks for the English teaching edition; no training or downloads.

Language rule (one-way, see AGENTS.md): the English edition must be pure English everywhere
a learner reads or types - code cells, Markdown prose, and the saved outputs shipped as
evidence. This scanner reads whole .ipynb files, so cell outputs are covered too. Chinese
masters may mix English freely; `scripts/check_parity.py` only counts those fragments.
"""
from pathlib import Path
import ast
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CJK = re.compile(r'[\u3400-\u9fff\uf900-\ufaff]')
# The course runner must be able to write Chinese runtime cells into the mirrored Chinese
# course, so Chinese literals are allowed in that one tool (recorded here on purpose).
BILINGUAL_TOOLS = {'scripts/execute_and_save.py'}



def main():
    problems, checked, notebooks = [], 0, 0
    paths = []
    for directory, folders, files in os.walk(ROOT):
        folders[:] = [name for name in folders if not name.startswith('.venv')
                      and name not in {'data', 'outputs', '__pycache__', 'logs', '.ipynb_checkpoints'}]
        paths.extend(Path(directory) / name for name in files)
    for path in paths:
        relative = path.relative_to(ROOT)
        if any(part.startswith('.venv') or part in {'data','outputs','__pycache__','logs','.ipynb_checkpoints'}
               for part in relative.parts):
            continue
        if not path.is_file() or path.suffix not in {'.py','.md','.ipynb','.json','.toml','.txt'}:
            continue
        if not relative.as_posix().isascii():
            problems.append(f'Non-ASCII filename: {relative}')
        text = path.read_text(encoding='utf-8')
        if CJK.search(text) and relative.as_posix() not in BILINGUAL_TOOLS:
            problems.append(f'CJK text in course source: {relative}')
        checked += 1
        markdown = []
        if path.suffix == '.ipynb':
            notebooks += 1
            nb = json.loads(text)
            try:
                import nbformat
                nbformat.validate(nb)
            except ImportError:
                pass
            for index, cell in enumerate(nb['cells']):
                source = ''.join(cell['source'])
                if cell['cell_type'] == 'code':
                    try:
                        ast.parse(source)
                    except SyntaxError as exc:
                        problems.append(f'{relative}, cell {index}: {exc}')
                    if any(out.get('output_type') == 'error' for out in cell.get('outputs', [])):
                        problems.append(f'Saved execution error: {relative}, cell {index}')
                else:
                    markdown.append(source)
        elif path.suffix=='.py':
            ast.parse(text)
        elif path.suffix=='.md':
            markdown.append(text)
        for source in markdown:
            source = re.sub(r'```[\s\S]*?```','',source)
            for link in re.findall(r'\]\(([^)]+)\)',source):
                if re.match(r'\w+://|#',link):
                    continue
                if not (path.parent/link.split('#')[0]).exists():
                    problems.append(f'Broken local link: {relative}: {link}')
    report = {'source_files_checked':checked,'notebooks':notebooks,'problems':problems,
              'scope':'Authored course sources; virtual environments, raw data, and generated outputs excluded.'}
    (ROOT/'reports').mkdir(exist_ok=True)
    (ROOT/'reports/static-checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    if problems:
        raise SystemExit(1)


if __name__=='__main__':
    main()
