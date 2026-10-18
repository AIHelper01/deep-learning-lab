"""Historical reproduction only: fetch the credential-free Rock Paper Scissors YOLO mirror and build the course export.

The mirror ships a LibreYOLO layout (``images/train`` plus ``labels/train``, and no test
split). This script caches it under ``data/rps-mirror`` and materializes the layout that
``common/detection_data.prepare_rps`` validates: ``train/``, ``valid/``, and ``test/``, each
with ``images/`` and ``labels/``, plus a rewritten ``data.yaml``. Re-running is a no-op.
"""
from pathlib import Path
import hashlib
import json
import shutil
import sys

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "common"))

REPO = "Xuban/rock-paper-scissors-roboflow"
API = f"https://huggingface.co/api/datasets/{REPO}/tree/main"
RESOLVE = f"https://huggingface.co/datasets/{REPO}/resolve/main"
CACHE = ROOT / "02-object-detection/data/rps-mirror"
EXPORT = ROOT / "02-object-detection/data/rock-paper-scissors"
SOURCES = ["https://universe.roboflow.com/rock-paper-scissors-2/rock-paper-scissors-bwev7",
           f"https://huggingface.co/datasets/{REPO}"]


def mirror_files():
    """List every file in the mirror, following the Hub pagination header."""
    rows = []
    response = requests.get(API, params={"recursive": "true", "paginate": "true"}, timeout=120)
    while True:
        rows.extend(response.json())
        link = response.headers.get("Link", "")
        if 'rel="next"' not in link:
            return [row for row in rows if row["type"] == "file"]
        response = requests.get(link.split(">")[0].strip("< "), timeout=120)


def download(remote, target, size=None):
    """Fetch one mirror file unless a cached copy of the listed size already exists."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and size is not None and int(size) == target.stat().st_size:
        return False
    response = requests.get(f"{RESOLVE}/{remote}", timeout=300)
    response.raise_for_status()
    target.write_bytes(response.content)
    return True


def adopt_legacy_cache():
    """Reuse a mirror-layout folder left behind by an earlier manual download."""
    if (EXPORT / "images" / "train").is_dir() and not CACHE.exists():
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(EXPORT), str(CACHE))
        print("Reused the earlier mirror download as the cache.")


def cache_mirror():
    """Download the mirror in its original layout, skipping complete files."""
    fetched = 0
    files = mirror_files()
    for row in files:
        if download(row["path"], CACHE / row["path"], row.get("size")):
            fetched += 1
    print(f"Cached mirror files: {len(files)} ({fetched} fetched now).")


def mirror_names():
    """Read the mirror class-name order, which the validator must keep unchanged."""
    cached = CACHE / "data.yaml"
    if not cached.exists():
        raise RuntimeError("The mirror cache has no data.yaml to read class names from.")
    names = yaml.safe_load(cached.read_text(encoding="utf-8"))["names"]
    if isinstance(names, dict):
        names = [names[key] for key in sorted(names)]
    return [str(name).strip().lower() for name in names]


def clamp_label(source, target):
    """Clip out-of-image bounding-box edges into the image, keeping the visible extent.

    The mirror carries at least one annotation whose box reaches 1.48 in normalized
    coordinates. The course validator rejects such rows, and the part of a box outside the
    image is not something a detector can learn, so the visible part is kept.
    """
    lines, clamped = [], 0
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        category, x, y, width, height = line.split()
        x, y, width, height = map(float, (x, y, width, height))
        left, top = max(x - width / 2, 0.0), max(y - height / 2, 0.0)
        right, bottom = min(x + width / 2, 1.0), min(y + height / 2, 1.0)
        if (left, top, right, bottom) != (x - width / 2, y - height / 2, x + width / 2,
                                          y + height / 2):
            clamped += 1
        width, height = max(right - left, 1e-4), max(bottom - top, 1e-4)
        lines.append(f"{category} {(left + right) / 2:.6f} {(top + bottom) / 2:.6f} "
                     f"{width:.6f} {height:.6f}")
    target.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return clamped


def build_export():
    """Materialize the train/valid/test course layout from the cached mirror."""
    train = sorted((CACHE / "images" / "train").glob("*"))
    if not train:
        raise RuntimeError("The mirror cache has no training images.")
    # The mirror has no test split, so hold half of its validation images back by the
    # deterministic order of the SHA-256 of each filename.
    ranked = sorted((CACHE / "images" / "val").glob("*"),
                    key=lambda path: hashlib.sha256(path.name.encode("utf-8")).hexdigest())
    if len(ranked) < 2:
        raise RuntimeError("The mirror validation split is too small to hold a test split out.")
    splits = {"train": train, "valid": ranked[:len(ranked) // 2], "test": ranked[len(ranked) // 2:]}
    copied = clamped = 0
    for split, images in splits.items():
        for image in images:
            label = CACHE / "labels" / ("train" if split == "train" else "val") / f"{image.stem}.txt"
            if not label.exists():
                raise RuntimeError(f"Missing annotation in the mirror cache: {label.name}")
            (EXPORT / split / "images").mkdir(parents=True, exist_ok=True)
            (EXPORT / split / "labels").mkdir(parents=True, exist_ok=True)
            image_target = EXPORT / split / "images" / image.name
            if not image_target.exists():
                shutil.copy2(image, image_target)
                copied += 1
            # Labels are rewritten on every run so re-clustering never leaves stale rows.
            clamped += clamp_label(label, EXPORT / split / "labels" / label.name)
    names = mirror_names()
    (EXPORT / "data.yaml").write_text(
        f"path: {EXPORT.as_posix()}\n"
        "train: train/images\nvalid: valid/images\ntest: test/images\n"
        "names:\n" + "".join(f"  {index}: {name}\n" for index, name in enumerate(names)),
        encoding="utf-8")
    (EXPORT / "provenance.json").write_text(json.dumps({
        "sources": SOURCES, "license": "CC BY 4.0", "class_order": names,
        "splits": {split: len(images) for split, images in splits.items()},
        "holdout_rule": "Mirror validation images sorted by SHA-256 of filename; the first "
                        "half became valid and the second half became test.",
        "boxes_clamped_into_image": clamped}, indent=2) + "\n",
        encoding="utf-8")
    print("Course export:", {split: len(images) for split, images in splits.items()},
          f"({copied} images copied, {clamped} label rows clamped).")


def main():
    adopt_legacy_cache()
    cache_mirror()
    build_export()
    from detection_data import prepare_rps
    prepared, counts = prepare_rps(EXPORT, ROOT / "02-object-detection/outputs/rps-legacy-data.yaml", require_course_source=False)
    print("Validator accepted:", dict(enumerate(prepared["names"])), counts)


if __name__ == "__main__":
    main()
