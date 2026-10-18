#!/usr/bin/env python3
"""把已执行 notebook 的真实输出内嵌回 notebook 本体（clear outputs 后仍可见）。

规则（与课程约定一致）：
- 文字输出 -> 语言对应的标签（中文 `**预期输出：**` / 英文 `**Expected output:**`）+ ```text 逐字摘录；
- 图片输出 -> 导出到模块的平行 assets 目录（<前缀>-1.png、<前缀>-2.png …），markdown 用相对路径引用；
- 生成的 markdown 单元带 `course-expected-output` 标签，可重复执行（先删后建）；
- 图注默认取该代码单元上方最近的 markdown 标题（自动中/英对应），也可在任务表里手写覆盖。

用法（仓库根目录）：
    ~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py                    # 全部任务
    ~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 01-image-classification
"""
from pathlib import Path
import argparse
import base64
import copy
import os
import re

import nbformat

ROOT = Path(__file__).resolve().parents[1]
TAG = "course-expected-output"
FENCE_SAFE = re.compile(r"\n```")
ABS_PATH = re.compile(r"(?:/Users/[^\s'\"]+?|[A-Za-z]:[\\/]+?)(?=deep-learning-lab)")

LABELS = {
    "zh": {
        "text": "**预期输出：**",
        "image": "**预期输出（图片）：**",
        "path_note": "（输出里的 `…` 代表运行本 notebook 时所在机器的仓库绝对路径前缀，你在自己机器上执行会看到自己的路径。）",
        "figure": "第 {n} 张输出图",
    },
    "en": {
        "text": "**Expected output:**",
        "image": "**Expected output (image):**",
        "path_note": "(Inside the quoted output `…` stands for the repository's absolute path prefix "
                     "on the machine that ran the notebook; yours will show your own path.)",
        "figure": "Output figure {n}",
    },
}


def fold_paths(text):
    return ABS_PATH.sub("…/", text)


def heading_caption(cells, index, figure_number, lang):
    """向上找最近的 markdown 标题作为图注；标题里的序号会被去掉。"""
    fallback = LABELS[lang]["figure"].format(n=figure_number)
    for cell in reversed(cells[:index]):
        if cell.cell_type != "markdown":
            continue
        lines = [line.strip() for line in cell.source.splitlines() if line.strip()]
        if not lines:
            continue
        title = lines[0].lstrip("#").strip()
        title = re.sub(r"^\d+[\.、]\s*", "", title)
        if not title:
            continue
        return title if lang == "zh" else title
    return fallback


def clean_text(value):
    if FENCE_SAFE.search(value):
        return value.replace("```", "'''")
    return value


def build_blocks(nb, job):
    """Return the markdown cells to insert, keyed by the code cell index they follow."""
    lang = job["lang"]
    labels = LABELS[lang]
    cells = nb.cells
    blocks = {}
    figure = 0
    used_paths = []
    for index, cell in enumerate(cells):
        if cell.cell_type != "code" or not cell.outputs:
            continue
        text_parts = []
        image_parts = []
        for output in cell.outputs:
            kind = output.output_type
            if kind in ("stream", "error"):
                raw = "".join(output.text) if kind == "stream" else \
                    "\n".join(output.get("traceback", []))
                if raw.strip():
                    text_parts.append(fold_paths(raw.rstrip()))
            elif kind == "execute_result":
                plain = output.get("data", {}).get("text/plain")
                if plain:
                    text_parts.append(fold_paths("".join(plain).rstrip()))
            elif kind == "display_data":
                png = output.get("data", {}).get("image/png")
                if not png:
                    continue
                figure += 1
                name = f"{job['prefix']}-{figure}.png"
                target = job["assets"] / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(base64.b64decode(png))
                relative = Path(job["relative_assets"]) / name
                caption = job.get("captions", {}).get(
                    figure, heading_caption(cells, index, figure, lang))
                image_parts.append(f"![{caption}]({relative.as_posix()})\n\n*{caption}*")
                used_paths.append(target)
        body = []
        if text_parts:
            body.append(labels["text"] + "\n\n```text\n" + clean_text("\n".join(text_parts)) + "\n```")
            if "…/" in "".join(text_parts):
                body.append(labels["path_note"])
        for part in image_parts:
            body.append(labels["image"] + "\n\n" + part)
        if body:
            blocks[index] = "\n\n".join(body)
    return blocks, figure


def apply_job(job):
    notebook_path = job["notebook"]
    if not notebook_path.is_file():
        return f"跳过（缺少文件）：{notebook_path}"
    nb = nbformat.read(notebook_path, as_version=4)
    nb.cells = [cell for cell in nb.cells if TAG not in cell.get("metadata", {}).get("tags", [])]
    blocks, figures = build_blocks(nb, job)
    rebuilt = []
    for index, cell in enumerate(nb.cells):
        rebuilt.append(cell)
        if index in blocks:
            rebuilt.append(nbformat.v4.new_markdown_cell(
                blocks[index], metadata={"tags": [TAG]}))
    nb.cells = rebuilt
    if job.get("intro"):
        nb.cells.insert(1, nbformat.v4.new_markdown_cell(job["intro"], metadata={"tags": [TAG]}))
    nbformat.write(nb, notebook_path)
    return f"{notebook_path.relative_to(ROOT)}：内嵌 {len(blocks)} 处文字块、{figures} 张图"


# 少数 notebook 的图注/前言是人工撰写的（并且 lesson 报告已按这些图片名引用），
# 在这里登记后由本脚本统一下发；未登记的 notebook 使用「文件名主干 + 最近标题」自动图注。
OVERRIDES = {
    "02-object-detection/notebooks/01-yolo26-rock-paper-scissors.ipynb": {
        "prefix": "rock-paper-scissors",
        "captions": {
            1: "训练曲线：课堂默认 10 轮，横轴是累计到该轮的秒数",
            2: "test 划分归一化混淆矩阵（10 轮后对角线已明显收紧）",
            3: "test 划分预测样例（白色为真值框，彩色为预测）",
            4: "第一张 test 图片的单图预测：`paper`，置信度 0.874",
        },
        "intro": "\n".join([
            "> **每个代码单元后面都跟着一个「预期输出」单元**：文字输出逐字摘录，图片以 `../assets/` "
            "相对路径引用。因此即使执行 **Kernel → Clear All Outputs**（或第一次打开时没有输出），"
            "也能对照本实验的真实结果；重新执行后两者应当一致。",
            ">",
            "> 这里保存的输出来自 **课堂默认 10 轮的全量数据实跑**：Apple 芯片 MPS、`seed=42`、"
            "`imgsz=320`、端到端 1163.89 s，test mAP50 **0.9410** / mAP50-95 **0.7467**，"
            "英文版同参数同种子跑出的成绩一致（1161.8 s）。",
            ">",
            "> 复现方式：把 `Rock-Paper-Scissors.v1i.yolo26.zip` 放进 `/workspace/DataSet/yolo/`，"
            "按本模块 `data/README.md` 的 cp 方式或下载方式导入，再在**未设置 `COURSE_EPOCHS`** "
            "的终端里用 `env_dl_uv` 内核重新运行。注意 MPS 上 Ultralytics 的确定性开关会命中没有确定性实现的 "
            "`index_put_with_accumulate_mps` 内核，所以整体一致，不保证逐位复现。",
        ]),
    },
    "02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb": {
        "prefix": "vehicle-counting",
        "captions": {
            1: "各划分标注框的类别分布（源划分未重采样）",
            2: "带框标注样本网格",
            3: "本次训练的曲线",
            4: "test 划分归一化混淆矩阵",
            5: "test 划分预测样例（蓝色 GT，青色预测）",
            6: "四张 test 图片的检测与计数",
            7: "跟踪帧与过线（黄线 y=320）",
        },
    },
    "english/02-object-detection/notebooks/01-yolo26-rock-paper-scissors.ipynb": {
        "prefix": "rock-paper-scissors",
        "captions": {
            1: "Training curves from this run (ten epochs, default classroom parameters)",
            2: "Normalized confusion matrix on the test split",
            3: "Prediction samples on the test split (white ground-truth boxes, coloured predictions)",
            4: "Single-image prediction on the first test image: `paper` at 0.874 confidence",
        },
        "intro": "\n".join([
            "> **Every code cell is followed by an \"Expected output\" cell**: text output is quoted "
            "verbatim and figures are referenced through `../assets/` relative paths, so the real "
            "results stay visible after **Kernel -> Clear All Outputs** (or on a first open). "
            "Re-running the notebook should reproduce them.",
            ">",
            "> The saved outputs here are the **default ten-epoch classroom run** on Apple silicon "
            "MPS (`seed=42`, 1161.8 s end to end, test mAP50 0.9410 / mAP50-95 0.7467). The Chinese "
            "edition runs the same defaults on the same machine, so each notebook should be read "
            "against its own quoted numbers.",
        ]),
    },
    "english/02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb": {
        "prefix": "vehicle-counting",
        "captions": {
            1: "Class distribution of annotation boxes per split (source splits, no resampling)",
            2: "Grid of annotated samples (the number inside each box is its class id)",
            3: "Training curves from this run (five epochs at imgsz 320, Apple silicon MPS)",
            4: "Normalised confusion matrix on the test split",
            5: "Prediction samples on the test split (blue ground truth, cyan predictions)",
            6: "Detection and counting on four test images",
            7: "Tracked frames and line crossings (yellow line at y=320)",
        },
    },
}


def discover_jobs(module):
    """自动发现中英两侧的 notebook，按文件名主干生成 assets 前缀。"""
    jobs = []
    for side, lang in ((ROOT, "zh"), (ROOT / "english", "en")):
        module_dir = side / module
        if not module_dir.is_dir():
            continue
        paths = [p for p in sorted(module_dir.rglob("*.ipynb"))
                 if "notebooks" in p.parts and "archive" not in p.parts
                 and ".ipynb_checkpoints" not in p.parts]
        for path in paths:
            owner = path.parent
            while owner.name in ("notebooks", "extensions"):
                owner = owner.parent
            assets = owner / "assets"
            job = {
                "notebook": path,
                "assets": assets,
                "relative_assets": Path(os.path.relpath(assets, path.parent)).as_posix(),
                "prefix": path.stem,
                "lang": lang,
            }
            override = OVERRIDES.get(path.relative_to(ROOT).as_posix())
            if override:
                job.update(copy.deepcopy(override))
            jobs.append(job)
    return jobs



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", action="append",
                        help="模块目录名，可重复；默认覆盖三个模块。")
    args = parser.parse_args()
    modules = args.module or ["01-image-classification", "02-object-detection",
                              "03-sentiment-analysis"]
    for module in modules:
        for job in discover_jobs(module):
            print(apply_job(job))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
