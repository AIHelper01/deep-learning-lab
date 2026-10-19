#!/usr/bin/env python3
"""从中文母本生成英文镜像 notebook（英文 Markdown + 英文用户可见文案）。

课程方向：中文课件（仓库根目录的模块树）是母本，`english/` 按下表逐单元镜像派生。

设计要点（与 `scripts/build_chinese_course.py` 对称）：
- Markdown 以“中文原文首行精确匹配”为键，代码以“去掉缩进后的中文原行精确匹配”为键；
  母本一改而译文表没跟上，构建直接报错，不会静默留下过期英文。
- 含中文的 Markdown 单元必须整元有译文；含中文的代码行必须逐行有译文，否则同样报错——
  `english/scripts/check_course.py` 不允许 `english/` 下出现任何汉字。
- 代码单元只改注释与用户可见文案，训练逻辑与母本一致，因此中英两侧的指标可以互相印证。
- 运行信息单元（course-runtime-info）与「预期输出」单元（course-expected-output）
  由各自语言的执行/内嵌脚本生成，不参与镜像翻译。

用法（仓库根目录）：
    uv run python scripts/build_english_course.py            # 生成
    uv run python scripts/build_english_course.py --check     # 只校验译文覆盖
"""
from pathlib import Path
import argparse
import ast
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from titanic_en import LINE_EN as TITANIC_LINE_EN
from titanic_en import MD_EN as TITANIC_MD_EN

CJK = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
# 生成单元：由执行器/内嵌脚本按语言各自产出，镜像时先摘掉。
GENERATED_TAGS = {"course-runtime-info", "course-expected-output"}
# 中文母本 -> 该课的英文译文表。新增中文母本课时在这里登记一张新表。
TABLES = {
    "00-machine-learning/notebooks/01_Titanic-Case.ipynb": {
        "md": TITANIC_MD_EN,
        "line": TITANIC_LINE_EN,
    },
}


def translate_markdown(key, source, tables, problems):
    """整元 Markdown：按中文单元首行查译文；纯 ASCII 单元原样透传。"""
    if not CJK.search(source):
        return source
    stripped = source.strip()
    heading = stripped.splitlines()[0].strip() if stripped else ""
    if heading in tables["md"]:
        return tables["md"][heading]
    if stripped in tables["md"]:      # 兼容以整段原文为键的写法
        return tables["md"][stripped]
    problems.append(f"{key}: 缺少英文译文（Markdown 单元首行）-> {heading[:70]}")
    return source


def translate_code(key, source, tables, problems, used):
    """逐行翻译代码：含中文的行必须在行级译文表里，缩进原样保留。"""
    lines = []
    for line in source.splitlines():
        if not CJK.search(line):
            lines.append(line)
            continue
        stripped = line.strip()
        if stripped not in tables["line"]:
            problems.append(f"{key}: 缺少英文译文（代码行）-> {stripped[:70]}")
            lines.append(line)
            continue
        used.add(stripped)
        lines.append(line[:len(line) - len(line.lstrip())] + tables["line"][stripped])
    return "\n".join(lines)


def build_notebook(key, problems):
    tables = TABLES[key]
    notebook = json.loads((ROOT / key).read_text(encoding="utf-8"))
    cells = [cell for cell in notebook["cells"]
             if not GENERATED_TAGS & set(cell.get("metadata", {}).get("tags", []))]
    used_lines = set()
    used_markdown = set()
    result = []
    for cell in cells:
        source = "".join(cell["source"])
        if cell["cell_type"] == "markdown":
            translated = translate_markdown(key, source, tables, problems)
            stripped = source.strip()
            heading = stripped.splitlines()[0].strip() if stripped else ""
            if heading in tables["md"]:
                used_markdown.add(heading)
            elif stripped in tables["md"]:
                used_markdown.add(stripped)
            result.append({"cell_type": "markdown", "metadata": cell.get("metadata", {}),
                           "source": translated})
            continue
        translated = translate_code(key, source, tables, problems, used_lines)
        try:
            ast.parse(translated)
        except SyntaxError as exc:
            problems.append(f"{key}: 生成的代码单元语法错误：{exc}")
        result.append({"cell_type": "code", "execution_count": None, "outputs": [],
                       "metadata": cell.get("metadata", {}), "source": translated})
    for heading in tables["md"]:
        if heading not in used_markdown:
            problems.append(f"{key}: Markdown 译文未被使用（母本可能已改动）：{heading[:70]}")
    for line in tables["line"]:
        if line not in used_lines:
            problems.append(f"{key}: 代码行译文未被使用（母本可能已改动）：{line[:70]}")

    metadata = {name: value for name, value in notebook.get("metadata", {}).items()
                if name != "execution_environment"}
    metadata["language"] = "en"
    metadata["derived_from"] = key
    notebook["cells"] = result
    notebook["metadata"] = metadata
    return notebook


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="只校验译文覆盖，不写文件")
    parser.add_argument("--force", action="store_true",
                        help="覆盖已带实跑输出的英文镜像（覆盖后必须重新执行并内嵌输出）")
    parser.add_argument("--only", action="append",
                        help="只处理文件名包含该子串的母本，可重复；与 --force 搭配重建单本镜像")
    args = parser.parse_args()
    problems, written = [], []
    keys = [key for key in TABLES if not args.only or any(needle in key for needle in args.only)]
    if not keys:
        problems.append(f"--only 没有匹配到任何母本：{args.only}")
    for key in keys:
        try:
            notebook = build_notebook(key, problems)
        except FileNotFoundError:
            problems.append(f"缺少中文母本：{key}")
            continue
        target = ROOT / "english" / key
        if not args.check and target.exists() and not args.force:
            saved = json.loads(target.read_text(encoding="utf-8"))
            executed = any(cell.get("outputs") or cell.get("execution_count")
                           for cell in saved.get("cells", []) if cell.get("cell_type") == "code")
            if executed:
                problems.append(f"{key}: 英文镜像已保存实跑输出，拒绝覆盖。"
                                "确需重建请加 --force，然后重新执行并内嵌输出")
                continue
        written.append(key)
        if not args.check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
                              encoding="utf-8")
    for key in written:
        print(("生成" if not args.check else "校验"), key)
    if problems:
        print("\n".join(dict.fromkeys(problems)))
        print(f"发现 {len(set(problems))} 个问题")
        return 1
    print(f"英文镜像{'生成' if not args.check else '校验'}完成：{len(written)} 本")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
