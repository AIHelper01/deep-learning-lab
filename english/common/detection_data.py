"""Validate a local YOLO detection export before classroom training."""
from pathlib import Path
import hashlib
import math
import re
import yaml

RPS_WORKSPACE = 'melikeavan'
RPS_PROJECT = 'rock-paper-scissors-ishcs'
RPS_VERSION = 1
RPS_SOURCE = f'https://universe.roboflow.com/{RPS_WORKSPACE}/{RPS_PROJECT}'
RPS_DIRECTORY = f'{RPS_PROJECT}-v{RPS_VERSION}'

VEHICLE_WORKSPACE = 'vehicle-counting-rtvul'
VEHICLE_PROJECT = 'vehicle-counting-tksu5'
VEHICLE_VERSION = 4
VEHICLE_SOURCE = f'https://universe.roboflow.com/{VEHICLE_WORKSPACE}/{VEHICLE_PROJECT}'
VEHICLE_DIRECTORY = f'{VEHICLE_PROJECT}-v{VEHICLE_VERSION}'
VEHICLE_CLASSES = ('truck', 'bicycle', 'bus', 'car', 'motorcycle')


def prepare_coco8(data_dir, output_yaml):
    """Prepare the official tiny detection fixture inside the course data directory."""
    import requests
    import zipfile
    from ultralytics.utils import ROOT as ULTRALYTICS_ROOT
    data_dir = Path(data_dir).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    target = data_dir / 'coco8'
    if not (target / 'images' / 'val').exists():
        archive = data_dir / 'coco8.zip'
        with requests.get('https://ultralytics.com/assets/coco8.zip', timeout=90) as response:
            response.raise_for_status()
            archive.write_bytes(response.content)
        with zipfile.ZipFile(archive) as zipped:
            for item in zipped.infolist():
                destination = (data_dir / item.filename).resolve()
                if not destination.is_relative_to(data_dir):
                    raise ValueError('Unsafe archive member path.')
            zipped.extractall(data_dir)
    config = yaml.safe_load((ULTRALYTICS_ROOT / 'cfg/datasets/coco8.yaml').read_text(encoding='utf-8'))
    config['path'] = target.as_posix()
    config.pop('download', None)
    output_yaml = Path(output_yaml)
    output_yaml.write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
    return output_yaml


def polygon_line_to_box(fields):
    """Convert one YOLO segmentation line to the detection box that encloses it."""
    coordinates = [float(v) for v in fields[1:]]
    xs, ys = coordinates[0::2], coordinates[1::2]
    left, right, top, bottom = min(xs), max(xs), min(ys), max(ys)
    return (int(float(fields[0])), (left + right) / 2, (top + bottom) / 2, right - left, bottom - top)


def prepare_yolo_export(export_dir, output_yaml, *, expected_names, expected_nc,
                     workspace=None, project=None, version=None, require_course_source=True,
                     normalize_segmentation_lines=False):
    """Validate a Roboflow YOLO export and write a course-ready data YAML."""
    polygon_lines = 0
    root = Path(export_dir).resolve()
    source = root / 'data.yaml'
    if not source.exists():
        raise FileNotFoundError(
            'Export the Rock Paper Scissors object-detection dataset in YOLO format '
            f'from {RPS_SOURCE}/dataset/{RPS_VERSION} and prepare it with scripts/fetch_rps.py. '
            'See the dataset instructions in this module README. '
            'A classification-only image collection is not sufficient.')
    config = yaml.safe_load(source.read_text(encoding='utf-8'))
    if require_course_source:
        origin = config.get('roboflow', {})
        official = (origin.get('workspace') == workspace
                    and origin.get('project') == project
                    and str(origin.get('version')) == str(version))
        if not official:
            raise ValueError(f'The course requires {workspace}/{project} dataset/{version}. '
                             'Missing or different Roboflow metadata; unverified archives are not accepted.')
    raw = config['names']
    if isinstance(raw, dict):
        raw = {int(key): value for key, value in raw.items()}
        if sorted(raw) != list(range(len(raw))):
            raise ValueError('Class IDs must be consecutive, starting at zero.')
        raw = [raw[i] for i in range(len(raw))]
    names = [str(name).strip().lower() for name in raw]
    if len(names) != expected_nc or set(names) != set(expected_names):
        raise ValueError(f'Expected exactly the classes {sorted(expected_names)}.')
    # Preserve the original ID order. Never alphabetically reorder annotation IDs.
    prepared = {'path': root.as_posix(), 'names': names, 'nc': expected_nc}
    seen = {}
    counts = {}
    for split, choices in {'train': ['train'], 'val': ['valid', 'val'], 'test': ['test']}.items():
        folder = next((root / name for name in choices if (root / name / 'images').is_dir()), None)
        if folder is None:
            raise ValueError(f'Missing image directory for the {split} split.')
        images = sorted(p for p in (folder / 'images').rglob('*')
                        if p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'})
        if not images:
            raise ValueError(f'The {split} split has no images.')
        boxes = 0
        for image in images:
            if re.search(r'[\u3400-\u9fff]', image.relative_to(root).as_posix()):
                raise ValueError('Use English filenames in the course dataset.')
            digest = hashlib.sha256(image.read_bytes()).hexdigest()
            if digest in seen and seen[digest] != split:
                raise ValueError('An identical image occurs in multiple splits. Re-split the export.')
            seen[digest] = split
            relative = image.relative_to(folder / 'images').with_suffix('.txt')
            label = folder / 'labels' / relative
            if not label.exists():
                raise ValueError(f'Missing annotation file: {label.name}')
            lines = label.read_text(encoding='utf-8').splitlines()
            if normalize_segmentation_lines and any(
                    len(line.split()) >= 7 and len(line.split()) % 2 == 1
                    for line in lines if line.strip()):
                normalised = []
                for line in lines:
                    if not line.strip():
                        continue
                    fields = line.split()
                    if len(fields) >= 7 and len(fields) % 2 == 1:
                        class_id, x, y, width, height = polygon_line_to_box(fields)
                        normalised.append(f'{class_id} {x} {y} {width} {height}')
                        polygon_lines += 1
                    else:
                        normalised.append(line)
                label.write_text('\n'.join(normalised) + '\n', encoding='utf-8')
                lines = normalised
            for line in lines:
                if not line.strip():
                    continue
                fields = line.split()
                if len(fields) != 5:
                    raise ValueError('Detection labels require class_id x_center y_center width height.')
                category = int(fields[0])
                x, y, width, height = map(float, fields[1:])
                if category not in range(expected_nc) or not all(math.isfinite(v) for v in (x,y,width,height)):
                    raise ValueError('Invalid category or non-finite bounding-box coordinate.')
                if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < width <= 1 and 0 < height <= 1):
                    raise ValueError('Bounding-box coordinates must be normalized to [0, 1].')
                if min(x-width/2,y-height/2) < -0.001 or max(x+width/2,y+height/2) > 1.001:
                    raise ValueError('A bounding box extends beyond the image boundary.')
                boxes += 1
        if boxes == 0:
            raise ValueError(f'The {split} split has no annotated objects.')
        prepared[split] = (folder / 'images').relative_to(root).as_posix()
        counts[split] = {'images': len(images), 'boxes': boxes}
    counts['segmentation_lines_normalised'] = polygon_lines
    output_yaml = Path(output_yaml)
    output_yaml.parent.mkdir(parents=True, exist_ok=True)
    output_yaml.write_text(yaml.safe_dump(prepared, sort_keys=False), encoding='utf-8')
    return prepared, counts


def prepare_rps(export_dir, output_yaml, *, require_course_source=True):
    """Validate the shared Rock Paper Scissors v1 export used by both courses."""
    return prepare_yolo_export(
        export_dir, output_yaml, expected_names={'rock', 'paper', 'scissors'}, expected_nc=3,
        workspace=RPS_WORKSPACE, project=RPS_PROJECT, version=RPS_VERSION,
        require_course_source=require_course_source)


def prepare_vehicle_counting(export_dir, output_yaml, *, require_course_source=True):
    """Validate the vehicle counting v4 export used by the traffic-counting lesson.

    Three source label files carry YOLO segmentation lines instead of detection boxes; they are
    rewritten to their enclosing box at import time and the count is reported for provenance.
    """
    return prepare_yolo_export(
        export_dir, output_yaml, expected_names=set(VEHICLE_CLASSES), expected_nc=len(VEHICLE_CLASSES),
        workspace=VEHICLE_WORKSPACE, project=VEHICLE_PROJECT, version=VEHICLE_VERSION,
        require_course_source=require_course_source, normalize_segmentation_lines=True)
