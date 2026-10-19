#!/usr/bin/env python3
"""从中文母本生成英文镜像 notebook（`english/` 的视觉与 NLP 课件）。

课程方向已翻转为「中文课件为母本，`english/` 为派生镜像」（见 AGENTS.md）。
本脚本据此反向工作：读取仓库根的中文母本，按 `scripts/course_en.py` 的译文表
生成 `english/` 镜像；`00-machine-learning` 仍走 `scripts/build_english_course.py`。

设计要点（与 `scripts/build_english_course.py` 对称）：
- Markdown 以“中文原文首行精确匹配”为键，代码以“去掉缩进后的中文原行精确匹配”为键；
  母本一改而译文表没跟上，构建直接报错，不会静默留下过期英文；表中未用上的条目同样报错。
- 引导单元、字体三行、数据集语言不同的结构性单元按整元精确替换（`course_en.py`）。
- 运行信息单元（course-runtime-info）与「预期输出」单元（course-expected-output）
  由各自语言的执行/内嵌脚本生成，不参与镜像翻译；同步时按位置保留英文侧原有的
  这类单元与仍一致的已保存输出。

用法（仓库根目录）：
    uv run python scripts/build_chinese_course.py --check     # 只校验：译文覆盖 + 镜像同步
    uv run python scripts/build_chinese_course.py             # 同步英文镜像（保留仍一致的已保存输出）
    uv run python scripts/build_chinese_course.py --force     # 整本重建英文镜像（清空输出，须重新执行并内嵌）
"""
from pathlib import Path
import argparse
import ast
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from course_en import (BOOT_BLOCK, FONT_BLOCK_LINES, MD_EN, MD_EN_BY_FILE,
                       LINE_EN, LINE_EN_BY_FILE, BLOCKS_EN_BY_FILE)

CJK = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
# 运行信息/预期输出单元由各自语言的执行与内嵌脚本生成，镜像时先摘掉。
GENERATED_TAGS = {"course-runtime-info", "course-expected-output"}

# 中文母本路径（仓库根）。01/03 两模块的 11 本课件全部以中文为母本。
MASTERS = [
    "01-image-classification/notebooks/01-lenet-mnist.ipynb",
    "01-image-classification/notebooks/02-lenet-cifar10.ipynb",
    "01-image-classification/notebooks/03-resnet-cifar10.ipynb",
    "01-image-classification/notebooks/extensions/04-lenet-custom-data.ipynb",
    "03-sentiment-analysis/pytorch/notebooks/01-nlp-overview.ipynb",
    "03-sentiment-analysis/pytorch/notebooks/02-word-embeddings.ipynb",
    "03-sentiment-analysis/pytorch/notebooks/03-lstm-sentiment.ipynb",
    "03-sentiment-analysis/pytorch/notebooks/04-pretrained-chinese-sentiment.ipynb",
    "03-sentiment-analysis/paddle/notebooks/01-nlp-overview.ipynb",
    "03-sentiment-analysis/paddle/notebooks/02-word-embeddings.ipynb",
    "03-sentiment-analysis/paddle/notebooks/03-lstm-sentiment.ipynb",
]

# 中文课的可选预训练课使用中文检查点，文件名如实描述；英文侧保留历史文件名，
# 配对关系同时记录在 scripts/check_parity.py 的别名表里。
EN_NAME_OVERRIDES = {
    "03-sentiment-analysis/pytorch/notebooks/04-pretrained-chinese-sentiment.ipynb":
        "03-sentiment-analysis/pytorch/notebooks/04-pretrained-english-sentiment.ipynb",
}


def en_target(master):
    return ROOT / "english" / EN_NAME_OVERRIDES.get(master, master)


def is_generated(cell):
    return bool(GENERATED_TAGS & set(cell.get("metadata", {}).get("tags", [])))


def split_lines(text):
    lines = text.splitlines(keepends=True)
    return lines if lines else [""]


def translate_markdown(master, source, md_table, used_md, problems):
    """整元 Markdown：按中文单元首行查译文；纯 ASCII 单元原样透传。"""
    if not CJK.search(source):
        return source
    stripped = source.strip()
    heading = stripped.splitlines()[0].strip() if stripped else ""
    if heading in md_table:
        used_md.add(heading)
        return md_table[heading]
    if stripped in MD_EN:      # 兼容以整段原文为键的写法
        used_md.add(stripped)
        return MD_EN[stripped]
    problems.append(f"{master}: 缺少英文译文（Markdown 单元首行）-> {heading[:70]}")
    return source


def translate_code(master, source, line_table, used_lines, problems):
    """逐行翻译代码：与英文行不一致的行必须在行级译文表里，缩进原样保留。"""
    lines = []
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped or (stripped not in line_table and stripped not in LINE_EN):
            lines.append(line)
            continue
        table = line_table if stripped in line_table else LINE_EN
        used_lines.add(stripped)
        lines.append(line[:len(line) - len(line.lstrip())] + table[stripped])
    return "\n".join(lines)


class Audit:
    """记录译文表中每条规则是否被母本用上；没用上即母本可能已改动。"""

    def __init__(self):
        self.boot_used = False
        self.font_used = False
        self.md_used = {m: set() for m in MASTERS}
        self.line_used = {m: set() for m in MASTERS}
        self.block_used = {m: set() for m in MASTERS}

def build_notebook(master, audit, problems):
    """从中文母本派生英文的可翻译单元列表（无生成单元、无输出载荷）。"""
    notebook = json.loads((ROOT / master).read_text(encoding="utf-8"))
    cells = [cell for cell in notebook["cells"] if not is_generated(cell)]
    md_table = dict(MD_EN)
    md_table.update(MD_EN_BY_FILE.get(master, {}))
    line_table = LINE_EN_BY_FILE.get(master, {})
    blocks = BLOCKS_EN_BY_FILE.get(master, {})
    result = []
    for cell in cells:
        source = "".join(cell["source"])
        if cell["cell_type"] == "markdown":
            translated = translate_markdown(master, source, md_table, audit.md_used[master], problems)
            if CJK.search(translated):
                problems.append(f"{master}: 英文 Markdown 仍含中文：{translated[:60]}")
            result.append({"cell_type": "markdown", "metadata": cell.get("metadata", {}),
                           "source": translated})
            continue
        if source in BOOT_BLOCK:
            source = BOOT_BLOCK[source]
            audit.boot_used = True
        else:
            stripped_source = "\n".join(line for line in source.splitlines()
                                        if line not in FONT_BLOCK_LINES)
            if stripped_source != source:
                source = stripped_source
                audit.font_used = True
        if source in blocks:
            audit.block_used[master].add(source)
            source = blocks[source]
        else:
            source = translate_code(master, source, line_table, audit.line_used[master], problems)
            if CJK.search(source):
                problems.append(f"{master}: 英文代码仍含中文：{source[:60]}")
            try:
                ast.parse(source)
            except SyntaxError as exc:
                problems.append(f"{master}: 生成的代码单元语法错误：{exc}")
        result.append({"cell_type": "code", "execution_count": None, "outputs": [],
                       "metadata": cell.get("metadata", {}), "source": source})
    return result


def derived_metadata(master, existing=None):
    """英文镜像的元数据：继承母本，但语言标记、派生指向与内核都归英文侧。"""
    zh = json.loads((ROOT / master).read_text(encoding="utf-8"))
    skip = {"execution_environment", "translated_from", "derived_from", "language"}
    if existing is not None:
        skip.add("kernelspec")  # 内核显示名等归各语言侧自己
    metadata = {name: value for name, value in zh.get("metadata", {}).items()
                if name not in skip}
    if existing is not None and "kernelspec" in existing:
        metadata["kernelspec"] = existing["kernelspec"]
    metadata["language"] = "en"
    metadata["derived_from"] = master
    return metadata


def dump_notebook(notebook, indent=1):
    return json.dumps(notebook, ensure_ascii=False, indent=indent) + "\n"


def file_indent(path):
    head = path.read_text(encoding="utf-8")[:200]
    match = re.search(r"\n( +)\"cells\"", head)
    return len(match.group(1)) if match else 1


def align_committed(master, problems):
    """读取英文镜像；返回 (整本, 可翻译单元列表)。缺文件时报错返回 None。"""
    target = en_target(master)
    if not target.exists():
        problems.append(f"{master}: 缺少英文镜像 english/{EN_NAME_OVERRIDES.get(master, master)}")
        return None
    committed = json.loads(target.read_text(encoding="utf-8"))
    translatable = [cell for cell in committed["cells"] if not is_generated(cell)]
    return committed, translatable


def sync_existing(master, built_cells, problems):
    """就地同步英文镜像的可翻译单元，保留生成单元与仍一致的已保存输出。"""
    target = en_target(master)
    aligned = align_committed(master, problems)
    if aligned is None:
        return False
    committed, translatable = aligned
    if len(translatable) != len(built_cells):
        problems.append(f"{master}: 单元数量不一致（英文可翻译 {len(translatable)}，"
                        f"母本派生 {len(built_cells)}）；结构性改动请用 --force 整本重建")
        return False
    changed = []
    cursor = -1
    for index, built_cell in enumerate(built_cells):
        while True:
            cursor += 1
            if not is_generated(committed["cells"][cursor]):
                break
        committed_cell = committed["cells"][cursor]
        if "".join(committed_cell["source"]) == built_cell["source"]:
            continue
        changed.append(index)
        committed_cell["source"] = split_lines(built_cell["source"])
        if committed_cell["cell_type"] == "code":
            committed_cell["outputs"] = []
            committed_cell["execution_count"] = None
    metadata = committed.setdefault("metadata", {})
    derived = derived_metadata(master, existing=metadata)
    metadata_changed = any(metadata.get(name) != value for name, value in derived.items())
    for name in ("translated_from",):
        if name in metadata:
            metadata.pop(name)
            metadata_changed = True
    metadata.update(derived)
    if changed or metadata_changed:
        target.write_text(dump_notebook(committed, file_indent(target)), encoding="utf-8")
        if changed:
            print(f"同步 {master}: 更新单元 {changed}（其已保存输出已清除，需重新执行并内嵌）")
    return bool(changed or metadata_changed)


def force_write(master, built_cells, written_notebooks):
    target = en_target(master)
    indent = file_indent(target) if target.exists() else 1
    old = json.loads(target.read_text(encoding="utf-8")) if target.exists() else None
    notebook = {"cells": built_cells,
                "metadata": derived_metadata(master, existing=(old or {}).get("metadata")),
                "nbformat": (old or {}).get("nbformat", 4),
                "nbformat_minor": (old or {}).get("nbformat_minor", 5)}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(dump_notebook(notebook, indent), encoding="utf-8")
    written_notebooks.append(master)


def check_sync(master, built_cells, problems):
    aligned = align_committed(master, problems)
    if aligned is None:
        return
    _, translatable = aligned
    if len(translatable) != len(built_cells):
        problems.append(f"{master}: 单元数量不一致（英文可翻译 {len(translatable)}，"
                        f"母本派生 {len(built_cells)}），请运行 build_chinese_course.py 同步")
        return
    for index, (committed_cell, built_cell) in enumerate(zip(translatable, built_cells)):
        if "".join(committed_cell["source"]) != built_cell["source"]:
            problems.append(f"{master}: 英文镜像第 {index} 个可翻译单元与母本派生结果不一致，"
                            "请运行 build_chinese_course.py 同步")


def executed_notebook(path):
    saved = json.loads(path.read_text(encoding="utf-8"))
    return any(cell.get("outputs") or cell.get("execution_count")
               for cell in saved.get("cells", []) if cell.get("cell_type") == "code")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="只校验译文覆盖与英文镜像同步，不写文件")
    parser.add_argument("--force", action="store_true",
                        help="整本重建英文镜像（清空已保存输出，之后必须重新执行并内嵌）")
    parser.add_argument("--only", action="append",
                        help="只处理母本路径包含该子串的课件，可重复；与 --force 搭配重建单本镜像")
    args = parser.parse_args()
    problems = []
    selected = [m for m in MASTERS if not args.only or any(needle in m for needle in args.only)]
    if not selected:
        print(f"--only 没有匹配到任何母本：{args.only}")
        return 1
    audit = Audit()
    written = []
    for master in selected:
        if not (ROOT / master).exists():
            problems.append(f"缺少中文母本：{master}")
            continue
        built_cells = build_notebook(master, audit, problems)
        target = en_target(master)
        if args.check:
            check_sync(master, built_cells, problems)
        elif args.force or not target.exists() or not executed_notebook(target):
            force_write(master, built_cells, written)
        elif sync_existing(master, built_cells, problems):
            written.append(master)
    if selected:
        if not audit.boot_used and not args.only:
            problems.append("引导单元替换一次都没命中（母本可能已改动）")
        if not audit.font_used and not args.only:
            problems.append("字体三行一次都没命中（母本可能已改动）")
    for master in selected:
        for heading in MD_EN_BY_FILE.get(master, {}):
            if heading not in audit.md_used[master]:
                problems.append(f"{master}: Markdown 译文未被使用（母本可能已改动）：{heading[:70]}")
        for line in LINE_EN_BY_FILE.get(master, {}):
            if line not in audit.line_used[master]:
                problems.append(f"{master}: 代码行译文未被使用（母本可能已改动）：{line[:70]}")
        for block in BLOCKS_EN_BY_FILE.get(master, {}):
            if block not in audit.block_used[master]:
                problems.append(f"{master}: 结构性替换未命中（母本可能已改动）：{block[:60]}")
    if problems:
        print("\n".join(dict.fromkeys(problems)))
        print(f"发现 {len(set(problems))} 个问题")
        return 1
    verb = "校验" if args.check else ("重建" if args.force else "同步")
    print(f"英文镜像{verb}完成：{len(selected)} 本"
          + ("" if args.check else f"（写入 {len(written)} 本）"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
