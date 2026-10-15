"""Validate a local YOLO detection export before classroom training."""
from pathlib import Path
import hashlib
import math
import re
import yaml


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


def prepare_rps(export_dir, output_yaml):
    root = Path(export_dir).resolve()
    source = root / 'data.yaml'
    if not source.exists():
        raise FileNotFoundError(
            'Export the Rock Paper Scissors object-detection dataset in YOLO format '
            'and place data.yaml, train/, valid/, and test/ under data/rock-paper-scissors. '
            'See the dataset instructions in this module README. '
            'A classification-only image collection is not sufficient.')
    config = yaml.safe_load(source.read_text(encoding='utf-8'))
    raw = config['names']
    if isinstance(raw, dict):
        raw = {int(key): value for key, value in raw.items()}
        if sorted(raw) != list(range(len(raw))):
            raise ValueError('Class IDs must be consecutive, starting at zero.')
        raw = [raw[i] for i in range(len(raw))]
    names = [str(name).strip().lower() for name in raw]
    if len(names) != 3 or set(names) != {'rock', 'paper', 'scissors'}:
        raise ValueError('Expected exactly the English classes rock, paper, scissors.')
    # Preserve the original ID order. Never alphabetically reorder annotation IDs.
    prepared = {'path': root.as_posix(), 'names': names, 'nc': 3}
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
            for line in label.read_text(encoding='utf-8').splitlines():
                if not line.strip():
                    continue
                fields = line.split()
                if len(fields) != 5:
                    raise ValueError('Detection labels require class_id x_center y_center width height.')
                category = int(fields[0])
                x, y, width, height = map(float, fields[1:])
                if category not in range(3) or not all(math.isfinite(v) for v in (x,y,width,height)):
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
    output_yaml = Path(output_yaml)
    output_yaml.parent.mkdir(parents=True, exist_ok=True)
    output_yaml.write_text(yaml.safe_dump(prepared, sort_keys=False), encoding='utf-8')
    return prepared, counts
