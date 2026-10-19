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
    ~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 01-image-classification \
        --include-archive --notebook 01-lenet-mnist-copy1                             # 只刷归档课件
"""
from pathlib import Path
import argparse
import base64
import copy
import hashlib
import os
import re

import nbformat

ROOT = Path(__file__).resolve().parents[1]
TAG = "course-expected-output"
FENCE_SAFE = re.compile(r"\n```")
ABS_PATH = re.compile(r"(?:/Users/[^\s'\"]+?|[A-Za-z]:[\\/]+?)(?=deep-learning-lab)")
# 告警行里的 ipykernel 临时文件路径同样是机器相关的绝对路径前缀，按同样的方式折叠。
IPYKERNEL_PATH = re.compile(r"(?:/private)?/(?:var/folders/[^\s'\"`]+?|tmp)/ipykernel_\d+/")
# 彩色终端输出里的 ANSI 控制符在 markdown 里只会变成乱码，摘录时剥掉；文字本身保持逐字。
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

LABELS = {
    "zh": {
        "text": "**预期输出：**",
        "image": "**预期输出（图片）：**",
        "path_note": "（输出里的 `…` 代表运行本 notebook 时所在机器的仓库绝对路径前缀，你在自己机器上执行会看到自己的路径。）",
        "kernel_path_note": "（输出里的 `…` 是 Jupyter 内核本次运行的临时目录，每台机器、每次运行都不同；告警本身可以忽略。）",
        "figure": "第 {n} 张输出图",
    },
    "en": {
        "text": "**Expected output:**",
        "image": "**Expected output (image):**",
        "path_note": "(Inside the quoted output `…` stands for the repository's absolute path prefix "
                     "on the machine that ran the notebook; yours will show your own path.)",
        "kernel_path_note": "(Inside the quoted output `…` is the Jupyter kernel's temporary directory for that "
                            "run, which differs per machine and per run; the warning itself is harmless.)",
        "figure": "Output figure {n}",
    },
}


def fold_paths(text):
    return IPYKERNEL_PATH.sub("…/", ABS_PATH.sub("…/", text))


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
    value = ANSI_ESCAPE.sub("", value)
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
        saw_repo_path = saw_kernel_path = False
        for output in cell.outputs:
            kind = output.output_type
            if kind in ("stream", "error"):
                raw = "".join(output.text) if kind == "stream" else \
                    "\n".join(output.get("traceback", []))
                if raw.strip():
                    text_parts.append(fold_paths(raw.rstrip()))
                    saw_repo_path = saw_repo_path or bool(ABS_PATH.search(raw))
                    saw_kernel_path = saw_kernel_path or bool(IPYKERNEL_PATH.search(raw))
            elif kind == "execute_result":
                plain = output.get("data", {}).get("text/plain")
                if plain:
                    text_parts.append(fold_paths("".join(plain).rstrip()))
                    saw_repo_path = saw_repo_path or bool(ABS_PATH.search("".join(plain)))
                    saw_kernel_path = saw_kernel_path or bool(IPYKERNEL_PATH.search("".join(plain)))
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
            if saw_repo_path:
                body.append(labels["path_note"])
            if saw_kernel_path:
                body.append(labels["kernel_path_note"])
        for part in image_parts:
            body.append(labels["image"] + "\n\n" + part)
        if body:
            blocks[index] = "\n\n".join(body)
    return blocks, figure


def block_id(job, key, content):
    """内容不变则单元 id 不变：重复内嵌不会在 `git diff` 里留下只换 id 的噪音。"""
    prefix = re.sub(r"[^A-Za-z0-9_-]", "-", job["prefix"])
    digest = hashlib.sha1(content.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-expected-{key}-{digest}"[:64]


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
                blocks[index], metadata={"tags": [TAG]}, id=block_id(job, index, blocks[index])))
    nb.cells = rebuilt
    if job.get("intro"):
        intro = job["intro"]
        nb.cells.insert(1, nbformat.v4.new_markdown_cell(intro, metadata={"tags": [TAG]},
                                                         id=block_id(job, "intro", intro)))
    nbformat.write(nb, notebook_path)
    return f"{notebook_path.relative_to(ROOT)}：内嵌 {len(blocks)} 处文字块、{figures} 张图"


# 少数 notebook 的图注/前言是人工撰写的（并且 lesson 报告已按这些图片名引用），
# 在这里登记后由本脚本统一下发；未登记的 notebook 使用「文件名主干 + 最近标题」自动图注。
OVERRIDES = {
    "01-image-classification/archive/legacy-notebooks/01-lenet-mnist.ipynb": {
        "captions": {
            7: "附录「炫酷版」系统：训练过程面板",
            8: "附录「炫酷版」系统：单张图片推理输出",
        },
        "intro": "\n".join([
            "> **每个代码单元后面都跟着一个「预期输出」单元**：文字输出逐字摘录，图片导出到本目录 `assets/` "
            "并以相对路径引用，因此执行 **Kernel → Clear All Outputs** 之后仍然看得见这次实跑的结果。",
            ">",
            "> 这里保存的输出来自 **课堂环境 `~/env_dl_uv`（Python 3.12.12 + PyTorch 2.14.1）的实跑**："
            "Apple 芯片 MPS、`seed=42`、全量 MNIST、3 轮，端到端 66.73 s，最佳 test 准确率 **98.32%**"
            "（加载 checkpoint 复测 98.32%），单图 `../assets/lenet-7.jpg` 预测 **5**。",
            ">",
            "> 这本与 `archive/01-lenet-mnist-copy1.ipynb` 是同一条流程、同一个种子，所以逐轮数字完全一致，"
            "差别只在末尾的附录单元。",
            ">",
            "> 本目录是历史归档：默认不参与课程执行，也不参与 `verify_saved_outputs.py` 的产出校验。"
            "重跑要显式加 `--include-legacy`（仓库根目录，先实跑、再内嵌）：",
            "> - `~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group vision --language zh-CN --cwd notebook --include-legacy --notebook legacy-notebooks/01-lenet-mnist.ipynb`",
            "> - `~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 01-image-classification --include-archive --include-legacy --notebook legacy-notebooks/01-lenet-mnist.ipynb`",
        ]),
    },
    "01-image-classification/archive/legacy-notebooks/03-resnet-cifar10.ipynb": {
        "captions": {
            1: "第六节 3 轮训练的 loss 曲线",
            2: "第六节 3 轮训练的 accuracy 曲线",
            3: "单图推理输入 `../assets/resnet-2.png`：预测 plane（飞机）",
            4: "「炫酷版」训练面板：loss、accuracy、验证 loss 与最终对比（它重新训练的 3 轮）",
        },
        "intro": "\n".join([
            "> **每个代码单元后面都跟着一个「预期输出」单元**：文字输出逐字摘录，图片导出到本目录 `assets/` "
            "并以相对路径引用，因此执行 **Kernel → Clear All Outputs** 之后仍然看得见这次实跑的结果。",
            ">",
            "> 这里保存的输出来自 **课堂环境 `~/env_dl_uv`（Python 3.12.12 + PyTorch 2.14.1）的实跑**："
            "Apple 芯片 MPS、ResNet18 用 torchvision 的 ImageNet 预训练权重（首次运行会联网下载 44.7 MB，"
            "进度条按原样摘录）、CIFAR-10 全量、图片 resize 到 224×224、batch 64、SGD(lr 0.01, momentum 0.9)、"
            "课堂默认 3 轮。端到端 **3897.96 s（约 65 分钟）**——两遍 3 轮训练，每轮约 10.6 分钟，"
            "这本比前两本慢一个数量级，原因就是 224×224 的输入。",
            ">",
            "> 第六节 test 准确率逐轮 **91.65% → 92.08% → 93.68%**；第九节「炫酷版」重新搭一个预训练 ResNet18 "
            "再训 3 轮（每轮约 652 s），train 85.30% → 92.20% → 93.93%，被它当验证集使用的 test 90.05% → 91.91% → "
            "90.99%，**最佳 91.91%（第 2 轮）**，权重写到 `../outputs/resnet18_cifar10/`（不入库）。"
            "注意它拿 test 选模型，这正是不推荐的做法，现行课程改用 validation。",
            ">",
            "> 单图 `../assets/resnet-2.png` 预测 **plane（飞机）**，softmax 首位 1.0000。",
            ">",
            "> 唯一被跳过的单元在「炫酷版」末尾：它加载 `models/resnet18_cifar10/best_model/"
            "resnet18_cifar10_best_epoch_003_acc_93.05.pth`，那份权重在旧服务器上训练、从未进入仓库，"
            "素材目录里也没有，所以 93.05% 这个成绩无法在本机复现，单元已标 `skip-execution`（见其上方说明）。",
            ">",
            "> 摘录时剥掉了彩色终端输出的 ANSI 颜色码，其余文字逐字保留。本目录是历史归档：默认不参与课程执行，"
            "也不参与 `verify_saved_outputs.py` 的产出校验。重跑要显式加 `--include-legacy`（仓库根目录，先实跑、再内嵌）：",
            "> - `~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group vision --language zh-CN --cwd notebook --include-legacy --notebook legacy-notebooks/03-resnet-cifar10.ipynb`",
            "> - `~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 01-image-classification --include-archive --include-legacy --notebook legacy-notebooks/03-resnet-cifar10.ipynb`",
        ]),
    },
    "01-image-classification/archive/legacy-notebooks/02-lenet-cifar10.ipynb": {
        "captions": {
            1: "本次 3 轮训练的 loss 曲线",
            2: "本次 3 轮训练的 accuracy 曲线",
            3: "单图推理输入：CIFAR-10 test 下标 44（第 45 张，label 0 = airplane）",
        },
        "intro": "\n".join([
            "> **每个代码单元后面都跟着一个「预期输出」单元**：文字输出逐字摘录，图片导出到本目录 `assets/` "
            "并以相对路径引用，因此执行 **Kernel → Clear All Outputs** 之后仍然看得见这次实跑的结果。",
            ">",
            "> 这里保存的输出来自 **课堂环境 `~/env_dl_uv`（Python 3.12.12 + PyTorch 2.14.1）的实跑**："
            "Apple 芯片 MPS、CIFAR-10 全量、课堂默认 3 轮，端到端 32.81 s，test 准确率逐轮 "
            "47.66% → 52.90% → **57.23%**；末尾单元加载 `../outputs/model-lenet-cifar10.pth` 对 "
            "`../assets/lenet/test_cifar10.png` 推理，预测 **飞机**，置信度 **0.789**。",
            ">",
            "> 素材说明：`../assets/lenet/test_cifar10.png` 原文件随旧课件丢失，本次按历史输出图片在 CIFAR-10 test 集里"
            "逐像素搜索还原：它与**下标 44（第 45 张，label 0 = airplane）逐像素完全一致**（次优候选误差 2006），"
            "也与本模块自带素材 `../assets/resnet-2.png` 像素相同——`03-resnet-cifar10.ipynb` 用的就是那张图，两处预测互相印证。",
            ">",
            "> 本目录是历史归档：默认不参与课程执行，也不参与 `verify_saved_outputs.py` 的产出校验。"
            "重跑要显式加 `--include-legacy`（仓库根目录，先实跑、再内嵌）：",
            "> - `~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group vision --language zh-CN --cwd notebook --include-legacy --notebook legacy-notebooks/02-lenet-cifar10.ipynb`",
            "> - `~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 01-image-classification --include-archive --include-legacy --notebook legacy-notebooks/02-lenet-cifar10.ipynb`",
        ]),
    },
    "01-image-classification/archive/legacy-notebooks/extensions/04-lenet-custom-data.ipynb": {
        "captions": {
            1: "第一节 3 轮训练的 loss 曲线",
            2: "第一节 3 轮训练的 accuracy 曲线",
            3: "单图推理输入 `../../assets/lenet-7.jpg`：预测 5",
            4: "第二节「炫酷版」训练面板：loss、accuracy、验证 loss 与最终对比",
            5: "加载 `lenet_mnist_final.pth` 之后再次推理同一张图：仍是 5",
        },
        "intro": "\n".join([
            "> **每个代码单元后面都跟着一个「预期输出」单元**：文字输出逐字摘录，图片导出到上层 "
            "`../assets/`（本文件在 `extensions/` 下，实跑图片与 01/02/03 落在同一个 `assets/` 目录）"
            "并以相对路径引用，因此执行 **Kernel → Clear All Outputs** 之后仍然看得见这次实跑的结果。",
            ">",
            "> 第一、二节的输出来自 **课堂环境 `~/env_dl_uv`（Python 3.12.12 + PyTorch 2.14.1）的实跑**："
            "Apple 芯片 MPS、全量 MNIST、课堂默认 3 轮，端到端 58.62 s。第一节 test 准确率逐轮 "
            "95.10% → 97.22% → **97.66%**；第二节「炫酷版」重新训练 3 轮（每轮约 8.5 s），"
            "train 89.07% → 96.18% → 97.09%，validation 95.53% → 97.04% → **97.07%（最佳，第 3 轮）**，"
            "权重写到 `../../outputs/lenet_mnist/`（不入库）。单图 `../../assets/lenet-7.jpg` 两次都预测 **5**。",
            ">",
            "> **第三节没有实跑**：本机没有 LEDNUM 数据集，那一节的代码单元全部标了 `skip-execution`，"
            "执行器原样跳过；原因、以及怎么补齐数据，见第三节开头的说明。因此那一节的单元下方没有「预期输出」，"
            "这是有意的，不代表跑通了。",
            ">",
            "> 摘录时剥掉了彩色终端输出的 ANSI 颜色码，其余文字逐字保留。本目录是历史归档：默认不参与课程执行，"
            "也不参与 `verify_saved_outputs.py` 的产出校验。重跑要显式加 `--include-legacy`（仓库根目录，先实跑、再内嵌）：",
            "> - `~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group vision --language zh-CN --cwd notebook --include-legacy --notebook legacy-notebooks/extensions/04-lenet-custom-data.ipynb`",
            "> - `~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 01-image-classification --include-archive --include-legacy --notebook legacy-notebooks/extensions/04-lenet-custom-data.ipynb`",
        ]),
    },
    "01-image-classification/archive/01-lenet-mnist-copy1.ipynb": {
        "captions": {
            1: "MNIST 训练集类别分布：10 个数字各自的样本数",
            2: "一个批次反归一化后的样本网格（标题是该图的标签）",
            3: "本次 3 轮训练的 loss 与 accuracy 曲线，train 与 test 同图对比",
            4: "test 集混淆矩阵：横轴为预测类别，纵轴为真实类别",
            5: "收集到的错误样本：标题依次是真值 T、预测 P 与置信度",
            6: "单图推理 `assets/lenet-7.jpg`：预测 5，置信度 0.9959",
        },
        "intro": "\n".join([
            "> **每个代码单元后面都跟着一个「预期输出」单元**：文字输出逐字摘录，图片导出到本目录 `assets/` "
            "并以相对路径引用，因此执行 **Kernel → Clear All Outputs** 之后仍然看得见这次实跑的结果。",
            ">",
            "> 这里保存的输出来自 **课堂环境 `~/env_dl_uv`（Python 3.12.12 + PyTorch 2.14.1）的实跑**："
            "Apple 芯片 MPS、`seed=42`、全量 MNIST、课堂默认 3 轮，端到端 37.22 s，最佳 test 准确率 "
            "**98.32%**（加载 checkpoint 复测同为 98.32%）。",
            ">",
            "> 与 `notebooks/` 里的课程 notebook 不同，本文件按开头写明的工作约定运行：**以 notebook 所在目录 "
            "`archive/` 为工作目录**，于是 `../data`、`../outputs` 落在 `01-image-classification/` 下，"
            "`assets/` 则是本目录（单图推理用的 `lenet-7.jpg` 就在这里）。",
            ">",
            "> 刷新方式（仓库根目录，先实跑、再内嵌）：",
            "> - `~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group vision --language zh-CN --cwd notebook --notebook 01-lenet-mnist-copy1`",
            "> - `~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 01-image-classification --include-archive --notebook 01-lenet-mnist-copy1`",
        ]),
    },
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


def discover_jobs(module, include_archive=False, include_legacy=False, only=None):
    """自动发现中英两侧的 notebook，按文件名主干生成 assets 前缀。"""
    jobs = []
    for side, lang in ((ROOT, "zh"), (ROOT / "english", "en")):
        module_dir = side / module
        if not module_dir.is_dir():
            continue
        paths = [p for p in sorted(module_dir.rglob("*.ipynb"))
                 if "notebooks" in p.parts and "archive" not in p.parts
                 and ".ipynb_checkpoints" not in p.parts]
        if include_archive:
            # 归档课件与 `execute_and_save.py` / `verify_saved_outputs.py` 口径一致：
            # archive/ 根下的课件参与实跑与内嵌，legacy-notebooks/ 仍是只读历史，不执行也不内嵌。
            paths.extend(sorted(p for p in (module_dir / "archive").rglob("*.ipynb")
                                if (include_legacy or "legacy-notebooks" not in p.parts)
                                and ".ipynb_checkpoints" not in p.parts))
        for path in paths:
            # 与 execute_and_save.py 一致：既接受文件名主干，也接受仓库相对路径片段。
            if only and path.stem not in set(only) \
                    and not any(match in path.relative_to(ROOT).as_posix() for match in only):
                continue
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
    parser.add_argument("--include-archive", action="store_true",
                        help="一并处理模块 archive/ 根下的课件。")
    parser.add_argument("--include-legacy", action="store_true",
                        help="连同 archive/legacy-notebooks/ 一起内嵌（需配合 --include-archive），"
                             "只用于已经在 env_dl_uv 里实跑复现过的历史课件。")
    parser.add_argument("--notebook", action="append",
                        help="只处理文件名主干匹配的 notebook，可重复。")
    args = parser.parse_args()
    modules = args.module or ["01-image-classification", "02-object-detection",
                              "03-sentiment-analysis"]
    for module in modules:
        for job in discover_jobs(module, args.include_archive, args.include_legacy, args.notebook):
            print(apply_job(job))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
