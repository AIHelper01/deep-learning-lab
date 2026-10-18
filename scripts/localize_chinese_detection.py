#!/usr/bin/env python3
"""把中文检测课 notebook 代码里的用户可见文案改成中文（幂等，可重复执行）。

只改文案，不改训练与统计逻辑；JSON 报告的键名保持英文，便于中英两侧机器可读对比。
每条规则必须命中，否则报错——避免母本改动后中文悄悄失效。

用法（仓库根目录）：
    ~/env_dl_uv/.venv/bin/python scripts/localize_chinese_detection.py
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

RPS_RULES = [
    ('print("Ultralytics version:", ultralytics.__version__)',
     'print("Ultralytics 版本：", ultralytics.__version__)'),
    ('print("Device:", DEVICE)',
     'print("计算设备：", DEVICE)'),
    ('print("SMOKE TEST ONLY: COCO8 pipeline check; not hand-gesture training.")',
     'print("这只是冒烟测试：用 COCO8 检查流程能否跑通，不是手势检测训练。")'),
    ('print("English class mapping:", dict(enumerate(config["names"])))',
     'print("类别映射：", dict(enumerate(config["names"])))'),
    ('print("Validated split sizes:", counts)',
     'print("校验后的划分规模：", counts)'),
    ('print(f"Epochs: {EPOCHS}; image size: {IMGSZ}; smoke: {SMOKE}")',
     'print(f"训练轮数：{EPOCHS} | 输入尺寸：{IMGSZ} | 冒烟测试：{SMOKE}")'),
    ('print("Saved checkpoint:", best.name)',
     'print("保存的权重：", best.name)'),
    ('print("Expected plot not found:", curves)',
     'print("未找到预期图表：", curves)'),
    ('print("Expected plot not found:", figure_path)',
     'print("未找到预期图表：", figure_path)'),
    ('print(f"{split} mAP50: {metrics.box.map50:.4f}")',
     'print(f"{split} 集 mAP50：{metrics.box.map50:.4f}")'),
    ('print(f"{split} mAP50-95: {metrics.box.map:.4f}")',
     'print(f"{split} 集 mAP50-95：{metrics.box.map:.4f}")'),
    ('print(f"Class: {prediction.names[int(box.cls.item())]}; confidence: {float(box.conf.item()):.3f}")',
     'print(f"类别：{prediction.names[int(box.cls.item())]}；置信度：{float(box.conf.item()):.3f}")'),
]

VEHICLE_RULES = [
    # The runtime-check cell is shared with the English edition through the Chinese master,
    # so its three user-visible strings need rules as well.
    ('"Select the Python 3.12 project kernel."',
     '"请选择项目的 Python 3.12 内核。"'),
    ('"Select the locked project environment."',
     '"请选择项目锁定的运行环境。"'),
    ('"Run mode:", \'Default classroom training parameters\'',
     '"运行模式：", \'课堂默认训练参数\''),
    ('"Python:"',
     '"Python："'),
    ('\'torch\' + ":"',
     '\'torch\' + "："'),
    ('"Ultralytics version:"',
     '"Ultralytics 版本："'),
    ('"Device:"',
     '"计算设备："'),
    ('"| epochs:"',
     '"| 训练轮数："'),
    ('"| imgsz:"',
     '"| 输入尺寸："'),
    ('"| smoke:"',
     '"| 冒烟测试："'),
    ('"SMOKE TEST ONLY: COCO8 pipeline check; not the vehicle experiment."',
     '"这只是冒烟测试：用 COCO8 检查流程能否跑通，不是车辆实验的成绩。"'),
    ('"Class mapping:"',
     '"类别映射："'),
    ('"Validated split sizes:"',
     '"校验后的划分规模："'),
    ('"Source:"',
     '"数据来源："'),
    ('"| license:"',
     '"| 许可："'),
    ('"Archive SHA-256:"',
     '"数据集压缩包 SHA-256："'),
    ('"not recorded"',
     '"未记录"'),
    ('"COCO8 smoke mode skips the vehicle label census."',
     '"COCO8 冒烟模式跳过车辆标注统计。"'),
    ('f"{split}: {sum(census.values())} boxes"',
     'f"{split} 划分：{sum(census.values())} 个标注框"'),
    ('"Annotation boxes"',
     '"标注框数量"'),
    ('"Vehicle class distribution per split (source splits kept unchanged)"',
     '"各划分的车辆类别分布（保持源划分，未重采样）"'),
    ('"COCO8 smoke mode skips the per-class sample grid."',
     '"COCO8 冒烟模式跳过每类样本网格。"'),
    ('"COCO8 smoke mode skips the zero-shot comparison."',
     '"COCO8 冒烟模式跳过零样本对比。"'),
    ('f"{\'image\':36} {\'GT\':>4} {\'pred\':>5} {\'abs error\':>9}"',
     'f"{\'图片\':<36} {\'真实\':>4} {\'预测\':>5} {\'绝对误差\':>9}"'),
    ('"Zero-shot mean absolute counting error:"',
     '"零样本平均绝对计数误差："'),
    ('"vehicles/image"',
     '"辆/张图片"'),
    ('"Training did not produce a best checkpoint."',
     '"训练没有产出 best 检查点。"'),
    ('"Saved checkpoint:"',
     '"已保存检查点："'),
    ('"Training curves from this run"',
     '"本次训练的损失与指标曲线"'),
    ('"Expected plot not found:"',
     '"未找到预期图表："'),
    ('f"{split} precision: {evaluation.box.mp:.4f}"',
     'f"{split} 划分精确率 precision：{evaluation.box.mp:.4f}"'),
    ('f"{split} recall:    {evaluation.box.mr:.4f}"',
     'f"{split} 划分召回率 recall：{evaluation.box.mr:.4f}"'),
    ('f"{split} mAP50:     {evaluation.box.map50:.4f}"',
     'f"{split} 划分 mAP50：{evaluation.box.map50:.4f}"'),
    ('f"{split} mAP50-95:  {evaluation.box.map:.4f}"',
     'f"{split} 划分 mAP50-95：{evaluation.box.map:.4f}"'),
    ('"Metric report written:"',
     '"指标报告已写出："'),
    ('f"{name} on the {split} split"',
     'f"{name}（{split} 划分）"'),
    ('"COCO8 smoke prediction classes:"',
     '"COCO8 冒烟模式预测到的类别："'),
    ('"COCO8 diagnostic prediction"',
     '"COCO8 诊断用预测结果"'),
    ('f"{image.name[:26]}\\nGT {sum(truth.values())} vs pred {tally[\'total\']}"',
     'f"{image.name[:26]}\\n真实 {sum(truth.values())} / 预测 {tally[\'total\']}"'),
    ('f"  (abs error {error})"',
     'f"（绝对误差 {error}）"'),
    ('f"{image.name}: predicted {tally[\'per_class\']} | ground truth {truth}"',
     'f"{image.name}：预测 {tally[\'per_class\']} | 真实 {truth}"'),
    ('"Fine-tuned mean absolute counting error:"',
     '"微调后平均绝对计数误差："'),
    ('"vehicles/image on these four test images"',
     '"辆/张图片（这四张测试图）"'),
    ('"Using video:"',
     '"使用的视频："'),
    ('"Synthetic clip written:"',
     '"已生成演示视频："'),
    ('"Ground truth crossings:"',
     '"真实过线数量："'),
    ('"Counting line:"',
     '"计数线位置："'),
    ('"| frames:"',
     '"| 总帧数："'),
    ('"| fps:"',
     '"| 帧率："'),
    ('"Analysed frames:"',
     '"实际分析帧数："'),
    ('"of declared"',
     '"，声明总帧数"'),
    ('f"{direction:8} crossings: {block[\'crossings\']:3d}  per class: {block[\'per_class\']}"',
     'f"{direction} 过线：{block[\'crossings\']:3d}  各类别：{block[\'per_class\']}"'),
    ('"Unique counted vehicles:"',
     '"已计数车辆（去重）："'),
    ('"| vehicle tracks ever seen:"',
     '"| 出现过的车辆跟踪轨迹数："'),
    ('"Flow:"',
     '"过线流向："'),
    ('"Ground-truth crossings:"',
     '"标注真实过线数量："'),
    ('f"-> detector/tracker deviation: {difference:+d}"',
     'f"，检测与跟踪偏差：{difference:+d}"'),
    ('f"frame {sample[\'frame\']}  (line y=320)"',
     'f"第 {sample[\'frame\']} 帧（计数线 y=320）"'),
    ('"COCO8 smoke mode does not write the traffic report."',
     '"COCO8 冒烟模式不会生成车流统计报告。"'),
]

TARGETS = [
    ("02-object-detection/notebooks/01-yolo26-rock-paper-scissors.ipynb", RPS_RULES),
    ("02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb", VEHICLE_RULES),
]


def main():
    problems = []
    for relative, rules in TARGETS:
        path = ROOT / relative
        notebook = json.loads(path.read_text(encoding="utf-8"))
        hits = {index: 0 for index in range(len(rules))}
        for cell in notebook["cells"]:
            if cell["cell_type"] != "code":
                continue
            source = "".join(cell["source"])
            updated = source
            for index, (old, new) in enumerate(rules):
                if old in updated:
                    hits[index] += updated.count(old)
                    updated = updated.replace(old, new)
            cell["source"] = updated
        applied = "".join(cell["source"] for cell in notebook["cells"]
                           if cell["cell_type"] == "code")
        already = 0
        for index, (old, new) in enumerate(rules):
            if hits[index]:
                continue
            if new in applied:
                already += 1     # 重复执行是安全的：替换文本已在 Notebook 里
                continue
            problems.append(f"{relative}: 规则未命中 -> {old[:70]}")
        note = f"（{already}/{len(rules)} 条此前已生效）" if already else ""
        print(f"已本地化{note}：{relative}")
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
