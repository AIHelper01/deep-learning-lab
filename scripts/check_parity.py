#!/usr/bin/env python3
"""中英课程对齐与输出语言检查：目录名、文件对齐、notebook 单元对齐、用户可见文案语言。

用法（仓库根目录）：

    python scripts/check_parity.py            # 打印并写入 english/reports/parity-checks.json

检查项：
1. 仓库内所有目录名与文件名必须是 ASCII（英文）。
2. 中文课程（根目录模块）与英文课程（english/ 模块）的 notebook、lesson、README 必须一一对应；
   `data/`、`outputs/` 里入库的 `README.md` 也算课程文档，同样要求成对。
3. 同名 notebook 的代码单元数量与 Markdown 单元数量应当一致。
4. 用户可见文案语言：中文 notebook 的 print/图表标题应为中文，英文 notebook 不得含中文。
5. 中文 notebook 的已保存输出不得包含执行错误。
"""
from pathlib import Path
import ast
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CJK = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
MODULES = ["00-machine-learning", "01-image-classification", "02-object-detection",
           "03-sentiment-analysis"]
SKIP_DIRS = {".git", ".venv", "__pycache__", ".ipynb_checkpoints", "data", "outputs",
             "assets", "logs", "node_modules", ".pytest_cache"}
# 产物目录里也有入库的说明文件（data/README.md、outputs/paddle/README.md 等）。
# 它们同样是课程文档，必须中英成对，所以从 SKIP_DIRS 里单独放行——只放行入了 Git 的 README.md，
# 本地产物与未跟踪的下载说明继续忽略。
DOC_DIRS = {"data", "outputs"}
# 单侧内容：键为（语言侧, 模块内相对路径），值是“不镜像”的原因，保证每处差异都是有意为之。
ONE_SIDED = {
    ("en", "02-object-detection/archive/01-yolo26-rps-legacy-executed.ipynb"):
        "English-side historical archive; the Chinese history is the original YOLO11 lesson kept in "
        "02-object-detection/notebooks/, a different artifact",
    ("zh", "02-object-detection/notebooks/01-yolo11-rock-paper-scissors.ipynb"):
        "Original Chinese PaddleYOLO/YOLO11 lesson, kept in notebooks/ at the owner's request for comparison; "
        "it needs that external project, is never executed, has no English twin, and is excluded from pairing",
    ("zh", "02-object-detection/archive/lessons/03-yolo-theory.md"):
        "Chinese historical courseware; english/02-object-detection/archive/README.md records why it stays untranslated",
    ("zh", "02-object-detection/archive/lessons/04-yolo-practice.md"):
        "Chinese historical courseware; english/02-object-detection/archive/README.md records why it stays untranslated",
}


# 中文侧遗留归档目录：同目录 README 说明原因，其 notebook 不参与中英配对。
LEGACY_DIR = "archive/legacy-notebooks/"
# 已经放回 notebooks/ 目录的历史件：保留可见，但仍按只读历史对待（不执行、不审计、不配对）。
HISTORY_IN_NOTEBOOKS = {"02-object-detection/notebooks/01-yolo11-rock-paper-scissors.ipynb"}
# 中英课程对齐但文件名如实描述各自使用的模型语言，这里登记配对关系。
ALIASES = {
    ("zh", "03-sentiment-analysis/pytorch/notebooks/04-pretrained-chinese-sentiment.ipynb"):
        "03-sentiment-analysis/pytorch/notebooks/04-pretrained-english-sentiment.ipynb",
    ("en", "03-sentiment-analysis/pytorch/notebooks/04-pretrained-english-sentiment.ipynb"):
        "03-sentiment-analysis/pytorch/notebooks/04-pretrained-chinese-sentiment.ipynb",
}


def pair_key(language, key):
    """把别名文件映射到配对另一侧的路径，使中英能够互认。"""
    return ALIASES.get((language, key), key)


def is_legacy(key):
    return LEGACY_DIR in key and key.endswith(".ipynb")


def is_archive(key):
    """archive/ 下只读历史：保留文件，但不参与课程审计。"""
    return "/archive/" in f"/{key}" or key.startswith("archive/")


def is_history(key):
    """只读历史：归档目录下，或已登记放回 notebooks/ 的旧课程件。"""
    return is_archive(key) or key in HISTORY_IN_NOTEBOOKS


# 中文课里允许保留英文文案的位置（必须写明原因，避免无声例外）。
ZH_ENGLISH_OUTPUT_ALLOWED = {
    "02-object-detection/notebooks/01-yolo26-rock-paper-scissors.ipynb":
        "输出来自上一次带数据集的实跑；本仓库当前没有 RPS 数据集，改写文案会让已保存输出失真。"
        "数据集到位后运行 execute_and_save --language zh-CN 即可得到中文输出，见 02-object-detection/data/README.md",
    "02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb":
        "剩余英文常量是输出文件名（vehicle-counting-metrics.json 等）与 COCO 类别名，"
        "属于数据标识而非用户可见文案；正文文案已全部中文化",
}


def one_sided_side(language, key, zh_set, en_set):
    """Return the documented side for a one-sided file, or an empty string."""
    if language == "zh" and key not in en_set and ("zh", key) in ONE_SIDED:
        return "zh"
    if language == "en" and key not in zh_set and ("en", key) in ONE_SIDED:
        return "en"
    return ""

PLOT_KEYWORDS = {"title", "set_title", "xlabel", "ylabel", "set_xlabel", "set_ylabel",
                 "suptitle", "set", "text", "annotate", "legend"}


def author_files():
    for path in ROOT.rglob("*"):
        if any(part in SKIP_DIRS or part.startswith(".venv") for part in path.relative_to(ROOT).parts):
            continue
        if path.is_file():
            yield path


def deliverable_paths():
    """返回"属于仓库内容"的文件集合：已入库的，以及没被 .gitignore 排除的新文件。

    产物目录里的下载包说明、本机缓存等被 .gitignore 排除的文件不会出现在这里，
    所以不会被误判成课程文档。不在 Git 仓库里时返回 None，跳过这项检查。
    """
    import subprocess
    result = subprocess.run(["git", "-C", str(ROOT), "ls-files",
                             "--cached", "--others", "--exclude-standard"],
                            capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return set(result.stdout.split())


DELIVERABLE = deliverable_paths()


def documented_product_readme(path):
    """data/ 与 outputs/ 里属于仓库的 README.md 是课程文档，纳入中英配对。"""
    if DELIVERABLE is None or path.name != "README.md":
        return False
    blocked = {part for part in path.relative_to(ROOT).parts if part in SKIP_DIRS}
    return bool(blocked) and blocked <= DOC_DIRS and path.relative_to(ROOT).as_posix() in DELIVERABLE


def module_files(base, module):
    root = base / module
    if not root.is_dir():
        return set()
    found = set()
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS or part.startswith(".venv") for part in path.relative_to(root).parts):
            if not documented_product_readme(path):
                continue
        elif not path.is_file():
            continue
        if path.suffix in {".ipynb", ".md"} and path.is_file():
            found.add(path.relative_to(root).as_posix())
    return found


def visible_strings(source):
    """Yield user-facing literals: print arguments and plot label keywords."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        def literals(node):
            """产出字面文案；跳过 f-string 的格式说明（如 `.4f`）。"""
            if isinstance(node, ast.FormattedValue):
                # f-string 的插值本身不是文案，只递归表达式，跳过 format_spec。
                yield from literals(node.value)
                return
            if isinstance(node, ast.Subscript):
                yield from literals(node.value)   # obj["key"] 里的键名不是文案
                return
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                yield node.value
                return
            for child in ast.iter_child_nodes(node):
                yield from literals(child)

        if name == "print":
            for arg in node.args:
                yield from literals(arg)
        elif name in PLOT_KEYWORDS:
            for arg in list(node.args) + [keyword.value for keyword in node.keywords]:
                yield from literals(arg)


def check_notebook(language, path, relative, problems, rows, archived=False):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    cells = notebook["cells"]
    # 运行时信息单元由执行器注入，不计入中英结构对齐，也不参与文案语言检查。
    cells = [c for c in cells
             if "course-runtime-info" not in c.get("metadata", {}).get("tags", [])
             and not (not archived and "course-expected-output"
                      in c.get("metadata", {}).get("tags", []))]
    code = [c for c in cells if c["cell_type"] == "code"]
    row = {"file": relative, "language": language,
           "code_cells": len(code), "markdown_cells": len(cells) - len(code),
           "executed_cells": sum(c.get("execution_count") is not None for c in code),
           "error_outputs": sum(o.get("output_type") == "error" for c in code
                                for o in c.get("outputs", []))}
    english_strings = []
    for index, cell in enumerate(code):
        source = "".join(cell["source"])
        for literal in visible_strings(source):
            text = literal.strip()
            if len(text) < 3 or "\n" in text and len(text) < 12:
                continue
            has_cjk = bool(CJK.search(text))
            if not any(character.isalpha() for character in text):
                continue                      # 纯符号/格式片段（如 `.4f`）不算文案
            if language == "zh" and archived:
                continue
            if language == "zh" and not has_cjk:
                english_strings.append(text[:70])
            if language == "en" and has_cjk:
                problems.append(f"Chinese text in English notebook output: {relative} cell {index}: {text[:40]}")
        try:
            ast.parse(source)
        except SyntaxError as exc:
            problems.append(f"Syntax error: {relative}, cell {index}: {exc}")
    if language == "zh" and relative in ZH_ENGLISH_OUTPUT_ALLOWED:
        allowed, english_strings = english_strings, []
        row["allowed_english_outputs"] = len(allowed)
    row["english_only_outputs"] = len(english_strings)
    if language == "zh" and english_strings:
        row["examples"] = english_strings[:6]
    rows.append(row)


def main():
    problems, rows = [], []

    for path in author_files():
        relative = path.relative_to(ROOT)
        if not all(part.isascii() for part in relative.parts):
            problems.append(f"Non-ASCII path: {relative}")

    pairs = []
    for module in MODULES:
        zh, en = module_files(ROOT, module), module_files(ROOT / "english", module)
        # 归一化：别名文件在两侧都算存在，配对才不会被误判为缺失。
        zh_all = {item for item in zh if not is_legacy(f"{module}/{item}")}
        def alias(item):
            key = f"{module}/{item}"
            mapped = pair_key("zh", key)
            return mapped[len(module) + 1:] if mapped != key else item

        zh_norm = {alias(item) for item in zh_all}
        en_norm = set(en)   # 配对方向由中文侧别名表给出（两侧文件名可能不同）
        for item in sorted(zh_norm | en_norm):
            key = f"{module}/{item}"
            in_zh, in_en = item in zh_norm, item in en_norm
            if not in_en and ("zh", key) in ONE_SIDED:
                pairs.append({"module": module, "file": item, "status": "zh-only",
                              "reason": ONE_SIDED[("zh", key)]})
            elif not in_zh and ("en", key) in ONE_SIDED:
                pairs.append({"module": module, "file": item, "status": "en-only",
                              "reason": ONE_SIDED[("en", key)]})
            elif not in_en:
                pairs.append({"module": module, "file": item, "status": "missing-in-english"})
                problems.append(f"Missing in English course: english/{module}/{item}")
            elif not in_zh:
                pairs.append({"module": module, "file": item, "status": "missing-in-chinese"})
                problems.append(f"Missing in Chinese course: {module}/{item}")
            else:
                pairs.append({"module": module, "file": item, "status": "paired"})

    for module in MODULES:
        for language, base in (("zh", ROOT), ("en", ROOT / "english")):
            for path in sorted((base / module).rglob("*.ipynb") if (base / module).is_dir() else []):
                if any(part in SKIP_DIRS or part.startswith(".venv")
                       for part in path.relative_to(base / module).parts):
                    continue
                relative = path.relative_to(base).as_posix()
                archived = is_history(relative)
                check_notebook(language, path, relative,
                               [] if archived else problems, rows, archived=archived)

    for row in rows:
        if row["error_outputs"] and not is_history(row["file"]):
            label = "English" if row["language"] == "en" else "Chinese"
            problems.append(f"{label} notebook has saved errors: {row['file']}")

    # 单元数量对齐：同一门课的同一本 notebook 必须逐单元对应。
    by_key = {}
    for row in rows:
        if "/notebooks/" not in f"/{row['file']}":
            continue                          # 只对齐课程 notebook
        if is_history(row["file"]):
            continue
        key = pair_key(row["language"], row["file"])
        by_key.setdefault(key, {})[row["language"]] = row
    for key, sides in sorted(by_key.items()):
        if "zh" not in sides or "en" not in sides:
            continue
        zh_row, en_row = sides["zh"], sides["en"]
        if (zh_row["code_cells"], zh_row["markdown_cells"]) != (en_row["code_cells"], en_row["markdown_cells"]):
            problems.append(
                f"单元数不对齐: {key} 中文 {zh_row['code_cells']}code/{zh_row['markdown_cells']}md"
                f" vs 英文 {en_row['code_cells']}code/{en_row['markdown_cells']}md")

    zh_rows = [row for row in rows if row["language"] == "zh" and row["english_only_outputs"]]
    report = {
        "notebooks_checked": sum(row["language"] == "zh" or row["language"] == "en" for row in rows),
        "pairs": pairs,
        "parity_problems": [p for p in problems
                            if "Missing in" in p or "不对齐" in p],
        "chinese_notebooks_with_english_outputs": [
            {"file": row["file"], "english_only_outputs": row["english_only_outputs"],
             "examples": row.get("examples", [])} for row in zh_rows],
        "chinese_notebooks_with_english_outputs_total":
            sum(row["english_only_outputs"] for row in zh_rows),
        "notebooks": rows,
        "problems": problems,
    }
    target = ROOT / "english/reports/parity-checks.json"
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "notebooks"},
                     indent=2, ensure_ascii=False))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
