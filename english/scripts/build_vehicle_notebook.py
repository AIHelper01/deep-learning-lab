"""Author the English vehicle-counting notebook from the Chinese master notebook.

The detection lesson is taught in both languages from one code path: the Chinese notebook in
``02-object-detection/notebooks/`` is the master for this experiment, its code cells already print
English (Ultralytics metric names and class names are English), and the English edition differs only in
prose plus the outputs directory. Keeping one master prevents the two editions from drifting apart.

Run from the repository root:

    python english/scripts/build_vehicle_notebook.py

The generated notebook has no outputs; execute it with
``python english/scripts/execute_and_save.py --group detection --notebook 02-yolo26-vehicle-counting``
and then refresh its expected-output cells with
``python 02-object-detection/scripts/embed_expected_outputs.py``.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT.parent / "02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb"
TARGET = ROOT / "02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb"
EXPECTED_OUTPUT_CELLS = "course-expected-output"

# English prose, in the order the master notebook's markdown cells appear.
MARKDOWN = [
    """# YOLO26: vehicle detection and traffic counting

This lesson goes one step beyond object detection: **from "how many vehicles are in this image" to
"how many vehicles passed during a time window"**. The dataset is the official
[vehicle-counting-rtvul / vehicle-counting-tksu5 v4](https://universe.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/dataset/4)
YOLO26 export (CC BY 4.0): 6,565 images in five classes, `0=truck, 1=bicycle, 2=bus, 3=car, 4=motorcycle`.
The importer lowercases class names at their original IDs, and three source lines that were segmentation
polygons were rewritten as their bounding boxes (recorded in `provenance.json`).

Three ideas that must not be mixed up:

| Task | Question | What it needs |
|---|---|---|
| Detection counting | How many vehicles are in this image | Per-frame boxes + a de-duplication rule |
| Traffic counting | How many vehicles passed | Tracking IDs + line-crossing logic |
| Flow rate | How many vehicles per minute | Crossings divided by video duration |

> **Every code cell is followed by an "Expected output" cell**: text is quoted verbatim and figures are
> exported to `assets/` and linked with relative paths, so the recorded results stay readable after
> **Kernel -> Clear All Outputs**. Re-running should reproduce them. The recorded run is the Apple silicon
> MPS execution of 2026-10-18 on the `env_dl_uv` kernel (5 epochs, 320 px, `seed=42`, 940.21 s end to end,
> and the Chinese edition under the same parameters and seed matches it cell for cell); the full write-up
> is the [run report](../lessons/05-vehicle-counting-run-report.md).

Place the dataset in the course data directory first. Classroom data is staged outside the repository in
DataSet (classroom mirror `/workspace/DataSet/yolo`); from the repository root:

```powershell
.\\english\\02-object-detection\\.venv\\Scripts\\python.exe .\\english\\scripts\\import_vehicle_counting.py --from-staging
.\\start-notebooks.ps1 -Module detection
```

On macOS/Linux the single uv environment `~/env_dl_uv` (Jupyter kernel `env_dl_uv`) replaces the launcher;
see [environment setup](../../docs/environment-setup.md). `COURSE_SMOKE=1` switches to COCO8 as a pure
pipeline check and is not the vehicle experiment; `COURSE_EPOCHS` only shortens training. The video defaults
to a short clip that `build_traffic_demo_video.py` composes from real vehicle crops in the dataset (every
vehicle appears once and crosses once, so there is a definite answer); set `TRAFFIC_VIDEO=<your.mp4>` to
analyse your own road video.""",
    """## 1. Verify the dataset and class mapping

Each YOLO row is `class_id x_center y_center width height`, normalised by image width and height. The
importer already checked the Roboflow source metadata, the class set, split independence, and duplicate
images across splits. Here we read the measured counts and keep "images" and "annotation boxes" apart -
traffic experiments care about object counts, not image counts.""",
    """## 2. Zero-shot baseline: what does inference without fine-tuning give?

A COCO pretrained model does not know this dataset's five class IDs, but it already knows vehicle classes
such as `car / bus / truck / motorcycle`. We map the COCO names onto the five course classes and compare
with this dataset's ground truth. The teaching point: **measure the untrained error first**, then decide
whether fine-tuning is worth it and where the counting error comes from.""",
    """## 3. Fine-tune YOLO26n

`yolo26n.pt` is downloaded on first use. Classroom defaults are 5 epochs, 320 px, batch 8 - about three
minutes per epoch on Apple silicon MPS, and remember `COURSE_EPOCHS=1` is a pipeline check, not a classroom
result. The per-iteration progress bar is suppressed; the loss and mAP curves are shown directly below.""",
    """## 4. Evaluate the fine-tuned checkpoint

Validation selects the settings, the test set is for final evaluation only. `precision` and `recall` mean
different things for traffic counting: false positives inflate the count, missed vehicles deflate it. The
per-class table shows which class fails most, usually distant cars and occluded vehicles.""",
    """## 5. Counting vehicles in images: "how many vehicles are in this frame"

Run whole-image inference with the fine-tuned weights, tally per class, and draw the boxes. Points to note:

- Tracking IDs are not needed within one image, but low-confidence jitter still has to be removed, so state
  the `conf` threshold.
- Only the five configured vehicle classes are counted; if one vehicle becomes two boxes, the count is too
  high, which is one source of counting error.
- Print the predicted count next to the annotated ground-truth count so the error is measurable, instead of
  judging by how nice the picture looks.""",
    """## 6. Counting traffic in video: tracking plus line crossing

Counting boxes frame by frame adds the same vehicle dozens of times, so traffic counting needs two things:

1. **Tracking** (`model.track`, ByteTrack) gives every vehicle a stable `tracker_id`;
2. **Line crossing**: take the sign of the box's bottom-edge midpoint (the vehicle's ground contact point)
   relative to the counting line; a sign flip counts as one crossing, counted once per vehicle and
   direction, so turning back does not double-count (see `common/traffic_counting.py`).

First validate the counter on the synthetic clip generated by `build_traffic_demo_video.py` (six vehicles,
each crossing once), then repeat the same pipeline on a real road video with `TRAFFIC_VIDEO=<your.mp4>`.""",
    """## 7. Use your own road video

The same `count_video()` works on real surveillance or dashcam video; only the counting line has to match
the resolution:

```python
TRAFFIC_VIDEO = Path("/path/to/your-road-video.mp4")
summary, frames = count_video(trained, TRAFFIC_VIDEO,
                              line=((0, 0.55 * 1080), (1920, 0.55 * 1080)), conf=0.25)
print(summary["forward"]["crossings"], summary["backward"]["crossings"], summary["flow"])
```

Tune in this order: fix `conf` first, then move the counting line, and only then touch tracker settings.
Every threshold changes the numbers, so any conclusion must state the line position, `conf`, and the
checkpoint used.""",
    """## Exercises and extensions

1. Lower `conf` from 0.25 to 0.10 and rerun the video: why does the crossing count change, and which
   classes start to jitter first?
2. Move the counting line up and down by 100 px and explain how the two directions change (where vehicles
   appear and disappear).
3. Compare detection-only counting (summing boxes per frame) with tracked counting and explain why traffic
   counting needs tracking.
4. Set `TRAFFIC_VIDEO` to a real clip and report the line position, `conf`, checkpoint, and per-class results
   together.
5. To cover more vehicle types (construction vehicles, scooters), extend the labels in the source dataset or
   collect new data, then import it through the same importer.

Sources and tools: [YOLO26 documentation](https://docs.ultralytics.com/models/yolo26/),
[ByteTrack tracking guide](https://docs.ultralytics.com/modes/track/),
[dataset v4](https://universe.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/dataset/4).""",
]

# The Chinese master also loads the Chinese chart-font helper and the Chinese course sys.path
# entry. The English edition needs neither, and english/ must stay free of Chinese characters,
# so both blocks are stripped through their ASCII anchors rather than by spelling out the
# Chinese lines here.
CHINESE_ONLY_BLOCKS = (
    re.compile(
        r"\n# [^\n]*\n"
        r'CHINESE_ROOT = COURSE\.parent if \(COURSE\.parent / "CHINESE_COURSE_ROOT"\)'
        r"\.is_file\(\) else None\n"
        r"if CHINESE_ROOT is not None:\n"
        r'    sys\.path\.insert\(0, str\(CHINESE_ROOT / "common"\)\)\n'
    ),
    re.compile(
        r"\nfrom course_zh import setup_chinese_fonts\n"
        r"print\(.*setup_chinese_fonts\(plt\)\)\n"
    ),
)

CODE_EDITS = (
    ('OUTPUT = COURSE.parent / "02-object-detection" / "outputs"',
     'OUTPUT = MODULE / "outputs"'),
)

# The Chinese master is localized last by ``scripts/localize_chinese_detection.py``, so its code
# cells now carry Chinese user-visible text. The English edition reverses exactly that table: the
# rules are read from the localizer instead of being copied here, so one edit keeps both
# editions in step and this file stays free of Chinese characters.
LOCALIZER = ROOT.parent / "scripts" / "localize_chinese_detection.py"


def reverse_localization_rules():
    import importlib.util

    spec = importlib.util.spec_from_file_location("course_localizer", LOCALIZER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return [(chinese, english) for english, chinese in module.VEHICLE_RULES]



def main():
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    cells = [cell for cell in master["cells"]
             if EXPECTED_OUTPUT_CELLS not in cell.get("metadata", {}).get("tags", [])]
    markdown = [cell for cell in cells if cell["cell_type"] == "markdown"]
    if len(markdown) != len(MARKDOWN):
        raise SystemExit(f"Master has {len(markdown)} markdown cells, translation table has {len(MARKDOWN)}. "
                         "Update MARKDOWN together with the Chinese master notebook.")
    DELOCALIZE = reverse_localization_rules()
    used = set()
    position = 0
    for cell in cells:
        if cell["cell_type"] == "markdown":
            cell["source"] = MARKDOWN[position].strip().splitlines(keepends=True)
            position += 1
            cell["metadata"] = {}
        else:
            source = "".join(cell["source"])
            for index, (old, new) in enumerate(DELOCALIZE):
                hits = source.count(old)
                if hits:
                    used.add(index)
                    source = source.replace(old, new)
            for index, (old, new) in enumerate(CODE_EDITS):
                hits = source.count(old)
                if hits:
                    used.add("edit %d" % index)
                    source = source.replace(old, new)
            for index, block in enumerate(CHINESE_ONLY_BLOCKS):
                source, hits = block.subn("", source)
                if hits:
                    used.add("block %d" % index)
            if any(ord(character) > 0x2fff for character in source):
                raise SystemExit("Derived English code cell still contains Chinese text.")
            cell["source"] = source.splitlines(keepends=True)
            cell["outputs"] = []
            cell["execution_count"] = None
    # Every rule must still describe the master: a rule that stops matching means the master
    # drifted and the English edition would silently keep stale or Chinese wording.
    missing = [index for index in range(len(DELOCALIZE)) if index not in used]
    for label in ("edit %d" % index for index in range(len(CODE_EDITS))):
        if label not in used:
            missing.append(label)
    for label in ("block %d" % index for index in range(len(CHINESE_ONLY_BLOCKS))):
        if label not in used:
            missing.append(label)
    if missing:
        raise SystemExit(f"{len(missing)} edits no longer match the Chinese master: {missing[:6]}. "
                         "Update this deriver together with 02-object-detection/notebooks/.")
    notebook = {"cells": cells,
                "metadata": master["metadata"] | {"kernelspec": {"display_name": "Python 3",
                                                                  "language": "python",
                                                                  "name": "python3"}},
                "nbformat": master["nbformat"], "nbformat_minor": master["nbformat_minor"]}
    notebook["metadata"].pop("execution_environment", None)
    import nbformat
    nbformat.validate(nbformat.from_dict(notebook))
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET.relative_to(ROOT.parent)} "
          f"({sum(c['cell_type'] == 'code' for c in cells)} code cells, {position} markdown cells)")


if __name__ == "__main__":
    main()
