"""Author the Chinese vehicle-counting (traffic flow) lesson notebook."""
from pathlib import Path
import json

MODULE = Path(__file__).resolve().parents[1]
TARGET = MODULE / 'notebooks/02-yolo26-vehicle-counting.ipynb'
EDITION = '2026-10-18'


def dedent(source):
    lines = source.split('\n')
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
    margin = min(indents) if indents else 0
    return '\n'.join(line[margin:] if line.strip() else '' for line in lines)


def md(source):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': dedent(source)}


def code(source, tags=()):
    return {'cell_type': 'code', 'execution_count': None, 'metadata': {'tags': list(tags)},
            'outputs': [], 'source': dedent(source)}


RUNTIME = code('''
    import sys
    from importlib.metadata import version
    from IPython import get_ipython
    get_ipython().run_line_magic("matplotlib", "inline")
    assert sys.version_info[:2] == (3, 12), "Select the Python 3.12 project kernel."
    assert version('torch').split("+")[0] == '2.14.1', "Select the locked project environment."
    print("Python:", sys.version.split()[0])
    print('torch' + ":", version('torch'))
    print("Run mode:", "default classroom training parameters")
''', tags=['course-runtime-info'])

CELLS = [
md(r'''
# YOLO26：车辆检测与车流量统计

本实验在目标检测基础上再走一步：**从“这张图里有几辆车”走到“一段时间内通过了多少辆车”**。
数据使用 [vehicle-counting-rtvul / vehicle-counting-tksu5 v4](https://universe.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/dataset/4)
的正式 YOLO26 导出（CC BY 4.0），6,565 张图，5 个类别 `0=truck, 1=bicycle, 2=bus, 3=car, 4=motorcycle`。
导入时按原编号只做小写规范化，并有 3 行标注在源包里是分割多边形，已改写为其外接检测框（数量记录在 `provenance.json`）。

三个必须分清的概念：

| 任务 | 问题 | 需要的信息 |
|---|---|---|
| 车辆检测计数 | 这张图里有几辆车 | 每帧检测框 + 去重规则 |
| 车流量统计 | 一段时间内通过几辆车 | 跟踪 ID + 过线判定 |
| 通行率 | 每分钟通过多少辆 | 车流量 ÷ 视频时长 |

先把数据集放到课程数据目录。数据统一在仓库外的 DataSet 暂存区（课堂镜像为 `/workspace/DataSet/yolo`），
仓库根目录执行：

```powershell
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\import_vehicle_counting.py --from-staging
.\start-notebooks.ps1 -Language zh-CN -Module detection
```

`COURSE_SMOKE=1` 会改用 COCO8 做纯链路检查，不代表车辆实验；`COURSE_EPOCHS` 只缩短训练轮数。
视频默认使用 `build_traffic_demo_video.py` 由数据集真实车辆裁剪合成的短片（每辆车只出现一次、只过一次线，
因此有确定答案），也可用 `TRAFFIC_VIDEO=<自己的.mp4>` 换成自己的道路视频。
'''),
RUNTIME,
code('''
    from pathlib import Path
    import os
    import sys

    # Find the English course root without relying on a specific working directory.
    start = Path.cwd().resolve()
    COURSE = next((p for p in [start, *start.parents]
                   if (p / "COURSE_ROOT").is_file()), None)
    if COURSE is None:
        COURSE = next((p / "english" for p in [start, *start.parents]
                       if (p / "english" / "COURSE_ROOT").is_file()), None)
    if COURSE is None:
        raise RuntimeError("Start Jupyter inside the project or the english directory.")
    sys.path.insert(0, str(COURSE / "common"))
    sys.path.insert(0, str(COURSE / "scripts"))

    # 中文课程专用模块（图表中文字体）放在仓库根的 common/ 下，英文课程目录保持全英文。
    CHINESE_ROOT = COURSE.parent if (COURSE.parent / "CHINESE_COURSE_ROOT").is_file() else None
    if CHINESE_ROOT is not None:
        sys.path.insert(0, str(CHINESE_ROOT / "common"))
    os.environ.setdefault("HF_HOME", str(COURSE / "data" / "huggingface"))
    os.environ.setdefault("TORCH_HOME", str(COURSE / "data" / "torch-cache"))
'''),
code('''
    import json
    import warnings

    from collections import Counter

    import numpy

    MODULE = COURSE / "02-object-detection"
    OUTPUT = COURSE.parent / "02-object-detection" / "outputs"
    # Keep Ultralytics settings local to this edition, before importing the package.
    os.environ["YOLO_CONFIG_DIR"] = str(OUTPUT / "ultralytics-config")
    import cv2
    import torch
    from ultralytics import YOLO, settings
    import ultralytics
    from ultralytics.utils import set_logging
    import matplotlib.pyplot as plt
    import yaml
    from detection_data import (prepare_vehicle_counting, VEHICLE_CLASSES, VEHICLE_DIRECTORY,
                                VEHICLE_SOURCE)
    from traffic_counting import (VEHICLE_CLASSES as TALLY_CLASSES, LineCrossingCounter,
                                  count_video, ground_truth_counts, tally_predictions)
    from build_traffic_demo_video import build as build_demo_video

    from course_zh import setup_chinese_fonts
    print("图表中文字体：", setup_chinese_fonts(plt))

    OUTPUT.mkdir(parents=True, exist_ok=True)
    SMOKE = os.environ.get("COURSE_SMOKE", "0") == "1"
    settings.update({"datasets_dir": str(MODULE / "data"),
                     "weights_dir": str(OUTPUT / "weights"),
                     "runs_dir": str(OUTPUT / "runs")})
    # Ultralytics redraws a per-iteration progress bar; inside a saved notebook every redraw
    # becomes a stored output record, so raise its log level and read the curve from results.png.
    set_logging(verbose=False)
    torch.set_num_threads(4)
    DEVICE = ("cuda" if torch.cuda.is_available()
              else "mps" if torch.backends.mps.is_available()
              else "cpu")

    # Ultralytics turns on warn-only determinism (seed plus torch.use_deterministic_algorithms).
    # On Apple Silicon the autograd kernel index_put_with_accumulate_mps has no deterministic
    # implementation, so that warning repeats once per epoch and buries the training log. It is
    # silenced here; the caveat stays real: on MPS a rerun matches in aggregate, not bit-for-bit.
    warnings.filterwarnings(
        "ignore",
        message="index_put_with_accumulate_mps does not have a deterministic implementation")
    PRETRAINED = "yolo11n.pt"      # COCO pretrained: zero-shot baseline with 80 classes.
    FINETUNE = "yolo26n.pt"        # Base weights fine-tuned here on the five vehicle classes.
    EPOCHS = int(os.environ.get("COURSE_EPOCHS", 1 if SMOKE else 5))
    IMGSZ = 64 if SMOKE else 320
    BATCH = 2 if SMOKE else 8
    COUNTING_LINE = ((0, 320), (640, 320))   # Data images are square 640x640 exports.
    print("Ultralytics version:", ultralytics.__version__)
    print("Device:", DEVICE, "| epochs:", EPOCHS, "| imgsz:", IMGSZ, "| smoke:", SMOKE)
'''),
md('''
## 1. 核对数据与类别映射

YOLO 每行标注为 `class_id x_center y_center width height`，坐标按图片宽高归一化。
导入器已核对 Roboflow 来源元数据、类别集合、划分独立性与跨集合重复图片；这里再读出实际数量，
并把「图片数」和「标注框数」分开看——车流量实验关心的是目标数量，不是图片数量。
'''),
code('''
    if SMOKE:
        from detection_data import prepare_coco8
        DATA_CONFIG = str(prepare_coco8(MODULE / "data", OUTPUT / "coco8-smoke-vehicle.yaml"))
        print("SMOKE TEST ONLY: COCO8 pipeline check; not the vehicle experiment.")
        EXPORT = None
    else:
        EXPORT = MODULE / "data" / VEHICLE_DIRECTORY
        DATA_CONFIG = OUTPUT / "vehicle-counting-data.yaml"
        config, counts = prepare_vehicle_counting(EXPORT, DATA_CONFIG)
        provenance = json.loads((EXPORT / "provenance.json").read_text(encoding="utf-8"))
        print("Class mapping:", dict(enumerate(config["names"])))
        print("Validated split sizes:", {k: v for k, v in counts.items()})
        print("Source:", provenance["source"], "| license:", provenance["license"])
        print("Archive SHA-256:", (provenance["archive_sha256"] or "not recorded")[:16], "...")
        DATA_CONFIG = str(DATA_CONFIG)
'''),
code('''
    if SMOKE:
        print("COCO8 smoke mode skips the vehicle label census.")
    else:
        def split_census(split):
            counter = Counter()
            for label in (EXPORT / split / "labels").glob("*.txt"):
                for line in label.read_text(encoding="utf-8").splitlines():
                    fields = line.split()
                    if len(fields) == 5:
                        counter[config["names"][int(fields[0])]] += 1
            return counter

        figure, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
        for axis, split in zip(axes, ("train", "valid", "test")):
            census = split_census(split)
            axis.bar(range(len(VEHICLE_CLASSES)), [census[name] for name in VEHICLE_CLASSES],
                     color="#2f6fb2")
            axis.set_xticks(range(len(VEHICLE_CLASSES)), VEHICLE_CLASSES, rotation=30)
            axis.set_title(f"{split}: {sum(census.values())} boxes")
        axes[0].set_ylabel("Annotation boxes")
        figure.suptitle("Vehicle class distribution per split (source splits kept unchanged)")
        plt.show()
'''),
code('''
    if SMOKE:
        print("COCO8 smoke mode skips the per-class sample grid.")
    else:
        def show_class_samples(per_class=2, columns=3):
            rows = max(1, columns - 1)
            figure, axes = plt.subplots(len(VEHICLE_CLASSES), rows,
                                        figsize=(4 * rows, 2.2 * len(VEHICLE_CLASSES)))
            axes = numpy.atleast_2d(axes)
            for row, name in enumerate(VEHICLE_CLASSES):
                shown = 0
                for image in sorted((EXPORT / "valid" / "images").glob("*.jpg")):
                    if shown == rows:
                        break
                    label = image.with_name(image.stem + ".txt")
                    if not label.exists():
                        continue
                    lines = [l.split() for l in label.read_text(encoding="utf-8").splitlines()
                             if len(l.split()) == 5]
                    hits = [f for f in lines if config["names"][int(f[0])] == name]
                    if not hits:
                        continue
                    picture = cv2.imread(str(image))
                    height, width = picture.shape[:2]
                    fields = hits[0]
                    x, y, w, h = map(float, fields[1:])
                    pad = 0.35
                    left = max(0, int((x - w / 2 - w * pad) * width))
                    right = min(width, int((x + w / 2 + w * pad) * width))
                    top = max(0, int((y - h / 2 - h * pad) * height))
                    bottom = min(height, int((y + h / 2 + h * pad) * height))
                    axis = axes[row, shown] if rows > 1 else axes[row]
                    axis.imshow(cv2.cvtColor(picture[top:bottom, left:right], cv2.COLOR_BGR2RGB))
                    axis.set_title(f"{name} ({shown + 1})", fontsize=10)
                    axis.axis("off")
                    shown += 1
                for extra in range(shown, rows):
                    axis = axes[row, extra] if rows > 1 else axes[row]
                    axis.axis("off")
            plt.tight_layout()
            plt.show()

        show_class_samples()
'''),
md('''
## 2. 零样本对照：不改权重直接推理会怎样

COCO 预训练模型不认识本数据集的 5 个类别编号，但它本来就有 `car / bus / truck / motorcycle`
等车辆类。先把 COCO 类名映射到本课程的 5 类，再和本数据集真值比较。
这一步的教学目的：**先量出“不训练的误差”有多大**，再判断微调是否值得，以及计数误差来自哪里。
'''),
code('''
    COCO_TO_COURSE = {"car": "car", "motorcycle": "motorcycle", "bus": "bus",
                      "truck": "truck", "pickup truck": "truck", "tractor": "truck"}

    def ground_truth(image):
        label = image.with_name(image.stem + ".txt")
        counter = Counter()
        if label.exists():
            for line in label.read_text(encoding="utf-8").splitlines():
                fields = line.split()
                if len(fields) == 5:
                    counter[config["names"][int(fields[0])]] += 1
        return dict(counter)

    def tally_to_course(boxes, names):
        raw = tally_predictions(boxes, names, vehicle_classes=tuple(COCO_TO_COURSE))
        merged = Counter()
        for coco_name, quantity in raw["per_class"].items():
            merged[COCO_TO_COURSE[coco_name]] += quantity
        return dict(merged), raw["total"]

    if SMOKE:
        print("COCO8 smoke mode skips the zero-shot comparison.")
    else:
        zero_shot = YOLO(OUTPUT / "weights" / PRETRAINED)
        samples = sorted((EXPORT / "test" / "images").glob("*.jpg"))[:6]
        rows = []
        for image in samples:
            result = zero_shot.predict(str(image), conf=0.25, imgsz=IMGSZ, device=DEVICE,
                                       verbose=False)[0]
            predicted, total = tally_to_course(result.boxes, zero_shot.names)
            truth = ground_truth(image)
            rows.append((image.name[:34], sum(truth.values()), total,
                         sum(abs(truth.get(k, 0) - predicted.get(k, 0))
                             for k in set(truth) | set(predicted))))
        print(f"{'image':36} {'GT':>4} {'pred':>5} {'abs error':>9}")
        for name, gt, pred, error in rows:
            print(f"{name:36} {gt:4d} {pred:5d} {error:9d}")
        print("Zero-shot mean absolute counting error:",
              round(sum(r[3] for r in rows) / len(rows), 2), "vehicles/image")
'''),
md('''
## 3. 微调 YOLO26n

`yolo26n.pt` 首次运行需要下载。课堂默认 5 轮、320 像素、batch 8；CPU 实跑请预留时间，
`COURSE_EPOCHS=1` 是链路检查而非课堂结果。进度条已降级，损失与 mAP 曲线在下面直接展示。
'''),
code('''
    weights = OUTPUT / "weights" / FINETUNE
    weights.parent.mkdir(parents=True, exist_ok=True)
    model = YOLO(str(weights))
    # Defaults are teaching parameters; runtime depends on the current dataset and hardware.
    results = model.train(data=DATA_CONFIG, epochs=EPOCHS, imgsz=IMGSZ, batch=BATCH, workers=0,
                          device=DEVICE, seed=42, deterministic=True, verbose=False,
                          project=str(OUTPUT / "runs"),
                          name="coco8-smoke-vehicle" if SMOKE else "vehicle-counting-v4-yolo26n",
                          exist_ok=False, plots=True)
    best = Path(model.trainer.best)
    if not best.exists():
        raise RuntimeError("Training did not produce a best checkpoint.")
    print("Saved checkpoint:", best)

    curves = Path(model.trainer.save_dir) / "results.png"
    if curves.exists():
        figure, axis = plt.subplots(figsize=(12, 8))
        axis.imshow(plt.imread(curves))
        axis.axis("off")
        axis.set_title("Training curves from this run")
        plt.show()
    else:
        print("Expected plot not found:", curves)
'''),
md('''
## 4. 评估微调后的权重

验证集用于挑设置，测试集只做最终评估；`precision` 与 `recall` 在车流量场景里的含义不同：
误检会虚增流量，漏检会低估流量。逐类结果告诉你哪一类最容易出错（远处小车与遮挡车辆通常最差）。
'''),
code('''
    trained = YOLO(str(best))
    if SMOKE:
        split, evaluation = "val", trained.val(data=DATA_CONFIG, split="val", device=DEVICE,
                                               imgsz=IMGSZ, workers=0, batch=BATCH,
                                               project=str(OUTPUT / "runs"), name="evaluation-smoke")
    else:
        split, evaluation = "test", trained.val(data=DATA_CONFIG, split="test", device=DEVICE,
                                                imgsz=IMGSZ, workers=0, batch=BATCH,
                                                project=str(OUTPUT / "runs"),
                                                name="evaluation-vehicle")
    print(f"{split} precision: {evaluation.box.mp:.4f}")
    print(f"{split} recall:    {evaluation.box.mr:.4f}")
    print(f"{split} mAP50:     {evaluation.box.map50:.4f}")
    print(f"{split} mAP50-95:  {evaluation.box.map:.4f}")
    per_class = {}
    ap_index = {int(c): i for i, c in enumerate(evaluation.box.ap_class_index)}
    evaluated_names = dict(enumerate(config["names"])) if not SMOKE else dict(evaluation.names)
    for class_id, name in evaluated_names.items():
        if SMOKE or class_id not in ap_index:
            per_class[name] = {"ap50": None, "ap50_95": None}
        else:
            position = ap_index[class_id]
            per_class[name] = {"ap50": float(evaluation.box.ap50[position]),
                               "ap50_95": float(evaluation.box.ap[position])}
    report = {"smoke_test": SMOKE, "evaluation_split": split,
              "dataset": "COCO8" if SMOKE else VEHICLE_DIRECTORY,
              "dataset_provenance": {} if SMOKE else provenance,
              "precision": float(evaluation.box.mp), "recall": float(evaluation.box.mr),
              "map50": float(evaluation.box.map50), "map50_95": float(evaluation.box.map),
              "per_class": per_class, "epochs": EPOCHS, "imgsz": IMGSZ,
              "ultralytics_version": ultralytics.__version__}
    (OUTPUT / ("smoke-vehicle-metrics.json" if SMOKE else "vehicle-counting-metrics.json")).write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    print("Metric report written:", OUTPUT / ("smoke-vehicle-metrics.json" if SMOKE
                                             else "vehicle-counting-metrics.json"))

    for name in ("confusion_matrix_normalized.png", "val_batch0_pred.jpg"):
        figure_path = Path(evaluation.save_dir) / name
        if figure_path.exists():
            figure, axis = plt.subplots(figsize=(10, 10))
            axis.imshow(plt.imread(figure_path))
            axis.axis("off")
            axis.set_title(f"{name} on the {split} split")
            plt.show()
        else:
            print("Expected plot not found:", figure_path)
'''),
md('''
## 5. 图片车流量：数清「这一帧里有几辆车」

用微调权重对整张图推理，按类别统计数量并画框。要点：

- 同一张图内不需要跟踪 ID，但仍要去掉低置信度抖动，所以 `conf` 阈值要写明。
- 只统计配置的 5 个车辆类别；万一一辆车被拆成两个框，数量就会偏大，这正是计数的误差来源之一。
- 把「模型预测数量」和「标注真值数量」并排打印，才能判断误差，而不是只看图好看。
'''),
code('''
    if SMOKE:
        from ultralytics.utils import ASSETS
        image = ASSETS / "bus.jpg"
        result = trained.predict(str(image), conf=0.25, imgsz=IMGSZ, device=DEVICE, verbose=False)[0]
        print("COCO8 smoke prediction classes:",
              tally_predictions(result.boxes, trained.names,
                                vehicle_classes=("car", "bus", "truck", "motorcycle")))
        plt.figure(figsize=(7, 6))
        plt.imshow(result.plot()[:, :, ::-1])
        plt.title("COCO8 diagnostic prediction"); plt.axis("off"); plt.show()
    else:
        grid = sorted((EXPORT / "test" / "images").glob("*.jpg"))[:4]
        figure, axes = plt.subplots(2, 2, figsize=(13, 12))
        errors = []
        for axis, image in zip(axes.ravel(), grid):
            result = trained.predict(str(image), conf=0.25, imgsz=IMGSZ, device=DEVICE,
                                     verbose=False)[0]
            tally = tally_predictions(result.boxes, trained.names, vehicle_classes=VEHICLE_CLASSES)
            truth = ground_truth(image)
            error = sum(abs(truth.get(k, 0) - tally["per_class"].get(k, 0))
                        for k in set(truth) | set(tally["per_class"]))
            errors.append(error)
            axis.imshow(result.plot()[:, :, ::-1])
            axis.set_title(f"{image.name[:26]}\\nGT {sum(truth.values())} vs pred {tally['total']}"
                           f"  (abs error {error})", fontsize=10)
            axis.axis("off")
            print(f"{image.name}: predicted {tally['per_class']} | ground truth {truth}")
        plt.tight_layout()
        plt.show()
        print("Fine-tuned mean absolute counting error:", round(sum(errors) / len(errors), 2),
              "vehicles/image on these four test images")
'''),
md('''
## 6. 视频车流量：跟踪 + 过线判定

逐帧数框会把同一辆车重复计入几十次，所以车流量必须做两件事：

1. **跟踪**（`model.track`，ByteTrack）给每辆车一个稳定 `tracker_id`；
2. **过线判定**：取框底边中点（车辆接地点）相对计数线的符号，符号翻转即视为过一次线，
   且每辆车每个方向只计一次，倒回去不会重复计数（实现见 `english/common/traffic_counting.py`）。

先用合成短片（`build_traffic_demo_video.py` 生成，已知 6 辆车各过一次线）验证计数器的正确性，
再用 `TRAFFIC_VIDEO=<自己的.mp4>` 换成真实道路视频做同一套流程。
'''),
code('''
    VIDEO = Path(os.environ.get("TRAFFIC_VIDEO", str(OUTPUT / "traffic-demo.mp4")))
    if VIDEO.exists():
        print("Using video:", VIDEO)
    else:
        VIDEO.parent.mkdir(parents=True, exist_ok=True)
        truth = build_demo_video(MODULE / "data" / VEHICLE_DIRECTORY, VIDEO, fps=12, frames=108)
        print("Synthetic clip written:", VIDEO)
        print("Ground truth crossings:", truth["expected_total_crossings"],
              truth["expected_vehicles_per_class"])
    ground_truth_path = VIDEO.with_suffix(".ground-truth.json")
    video_truth = json.loads(ground_truth_path.read_text(encoding="utf-8")) if ground_truth_path.exists() else None
    if video_truth:
        print("Counting line:", video_truth["counting_line"], "| frames:", video_truth["frames"],
              "| fps:", video_truth["fps"])
'''),
code('''
    summary, frames = count_video(trained, VIDEO, COUNTING_LINE, conf=0.25,
                                  imgsz=416 if not SMOKE else 64, device=DEVICE,
                                  vehicle_classes=VEHICLE_CLASSES if not SMOKE else TALLY_CLASSES,
                                  annotated_frames=(12, 30, 48))
    print("Analysed frames:", summary["frames_analysed"], "of declared", summary["declared_frames"],
          "| fps:", summary["fps"])
    for direction in ("forward", "backward"):
        block = summary[direction]
        print(f"{direction:8} crossings: {block['crossings']:3d}  per class: {block['per_class']}")
    print("Unique counted vehicles:", summary["unique_vehicles_seen"],
          "| vehicle tracks ever seen:", summary["tracks_observed"])
    print("Flow:", summary["flow"])
    if video_truth:
        difference = summary["flow"]["total_crossings"] - video_truth["expected_total_crossings"]
        print("Ground-truth crossings:", video_truth["expected_total_crossings"],
              f"-> detector/tracker deviation: {difference:+d}")

    figure, axes = plt.subplots(1, max(1, len(frames)), figsize=(5 * max(1, len(frames)), 5))
    axes = list(numpy.atleast_1d(axes))
    for axis, sample in zip(axes, frames):
        axis.imshow(sample["rgb"])
        axis.set_title(f"frame {sample['frame']}  (line y=320)", fontsize=10)
        axis.axis("off")
    plt.tight_layout()
    plt.show()
'''),
md('''
## 7. 换成你自己的道路视频

同一个 `count_video()` 可以直接处理真实监控/行车记录仪视频，只需要按画面分辨率调整计数线：

```python
TRAFFIC_VIDEO = Path("/path/to/your-road-video.mp4")
summary, frames = count_video(trained, TRAFFIC_VIDEO,
                              line=((0, 0.55 * 1080), (1920, 0.55 * 1080)), conf=0.25)
print(summary["forward"]["crossings"], summary["backward"]["crossings"], summary["flow"])
```

调参顺序建议：先固定 `conf`，再调计数线位置，最后才动跟踪器参数。判定阈值一变，
流量数字就变，所以报告结论时必须同时写出线的位置、`conf` 与模型权重。
'''),
code('''
    if SMOKE:
        print("COCO8 smoke mode does not write the traffic report.")
    else:
        traffic_report = {"video": summary["video"], "video_is_synthetic": video_truth is not None,
                          "model_checkpoint": str(best), "conf": 0.25, "tracker": "bytetrack.yaml",
                          "counting_line": summary["counting_line"],
                          "fps": summary["fps"], "frames_analysed": summary["frames_analysed"],
                          "counts": {d: summary[d] for d in ("forward", "backward")},
                          "unique_vehicles_counted": summary["unique_vehicles_seen"],
                          "vehicle_tracks_observed": summary["tracks_observed"],
                          "flow": summary["flow"],
                          "ground_truth": video_truth and video_truth["expected_total_crossings"],
                          "note": "Synthetic clip: every spawned vehicle crosses once, so the "
                                  "deviation measures detection and tracking quality, not traffic."}
        (OUTPUT / "vehicle-flow-report.json").write_text(json.dumps(traffic_report, indent=2),
                                                         encoding="utf-8")
        print(json.dumps({k: traffic_report[k] for k in
                          ("counts", "unique_vehicles_counted", "flow")}, indent=2, ensure_ascii=False))
'''),
md('''
## 练习与延伸

1. 把 `conf` 从 0.25 降到 0.10 再跑一次视频：过线数为什么会变，哪些类别先出现抖动？
2. 把计数线上下移动 100 像素，观察两个方向的车流量如何变化，解释原因（车辆出现/消失的位置）。
3. 只用检测不用跟踪（逐帧累加框数），对比两种口径的数字差距，说明为什么车流量必须跟踪。
4. 用 `TRAFFIC_VIDEO` 换一段真实视频，把线位置、`conf`、权重和逐类结果一起写进结论。
5. 想覆盖更多车型（如工程车、电动车），需要在原数据集补充标注或另找数据，再按同一导入流程入库。

来源与工具：[YOLO26 文档](https://docs.ultralytics.com/models/yolo26/)、
[ByteTrack 跟踪文档](https://docs.ultralytics.com/modes/track/)、
[数据集 v4](https://universe.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/dataset/4)。
'''),
]


def main():
    notebook = {'cells': CELLS,
                'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python',
                                            'name': 'python3'},
                             'language_info': {'name': 'python'},
                             'course': {'language': 'zh-CN', 'edition': EDITION}},
                'nbformat': 4, 'nbformat_minor': 5}
    if TARGET.exists():
        existing = json.loads(TARGET.read_text(encoding='utf-8'))
        if any(cell.get('execution_count') is not None for cell in existing['cells']):
            raise SystemExit('Executed notebook exists. Edit it in place to preserve saved outputs.')
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('Wrote', TARGET, 'with', len(CELLS), 'cells')


if __name__ == '__main__':
    main()
