"""Import the vehicle counting YOLO export into the course data directory.

Datasets are staged outside the repository in a DataSet folder (``/workspace/DataSet`` on the
classroom images). This helper copies an official Roboflow YOLO26 export from that staging
area into the course, validates it, and records provenance. It never downloads anything by
itself: Roboflow requires a signed-in account, so download the ZIP into the DataSet folder
first and then run this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import yaml

COURSE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(COURSE / 'common'))
from detection_data import (VEHICLE_CLASSES, VEHICLE_DIRECTORY, VEHICLE_PROJECT,  # noqa: E402
                            VEHICLE_SOURCE, VEHICLE_VERSION, VEHICLE_WORKSPACE,
                            prepare_vehicle_counting)

DESTINATION = COURSE / '02-object-detection' / 'data' / VEHICLE_DIRECTORY
DEFAULT_STAGING = Path('/workspace/DataSet/yolo')
ARCHIVE_GLOB = 'vehicle counting.v*.yolo26.zip'


def find_staged_archive(staging: Path) -> Path | None:
    """Return the newest official ZIP inside the DataSet staging folder."""
    candidates = sorted(staging.glob(ARCHIVE_GLOB), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def extract_archive(archive: Path, folder: Path) -> None:
    with zipfile.ZipFile(archive) as zipped:
        for item in zipped.infolist():
            if not (folder / item.filename).resolve().is_relative_to(folder):
                raise ValueError('Unsafe archive path.')
        zipped.extractall(folder)


def prepare_export(source: Path, destination: Path = DESTINATION,
                   archive_sha256: str | None = None,
                   source_label: str | None = None) -> tuple[list[str], dict]:
    """Validate export identity and labels, then import into a fresh isolated directory."""
    if destination.exists():
        raise FileExistsError(f'Refusing to overwrite or merge an existing export: {destination}')
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Source and destination must be separate, non-nested directories.')
    config = yaml.safe_load((source / 'data.yaml').read_text(encoding='utf-8'))
    origin = config.get('roboflow', {})
    if (origin.get('workspace') != VEHICLE_WORKSPACE or origin.get('project') != VEHICLE_PROJECT
            or str(origin.get('version')) != str(VEHICLE_VERSION)):
        raise ValueError(f'Export metadata must identify {VEHICLE_SOURCE}/dataset/{VEHICLE_VERSION}.')
    raw = config['names']
    if isinstance(raw, dict):
        raw = {int(k): v for k, v in raw.items()}
        if sorted(raw) != list(range(len(raw))):
            raise ValueError('Expected consecutive source class IDs starting at zero.')
        raw = [raw[i] for i in range(len(raw))]
    names = [str(name).strip().lower() for name in raw]
    if len(names) != len(VEHICLE_CLASSES) or set(names) != set(VEHICLE_CLASSES):
        raise ValueError(f'Expected exactly the classes {sorted(VEHICLE_CLASSES)}.')
    config['names'] = names
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='vehicle-import-', dir=destination.parent) as temporary:
        staged = Path(temporary) / 'export'
        shutil.copytree(source, staged)
        (staged / 'data.yaml').write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
        prepared, counts = prepare_vehicle_counting(staged, Path(temporary) / 'validated.yaml')
        for key in ('train', 'val', 'test'):
            config[key] = prepared[key]
        config['path'] = str(destination)
        (staged / 'data.yaml').write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
        (staged / 'provenance.json').write_text(json.dumps({
            'source': VEHICLE_SOURCE, 'version': VEHICLE_VERSION, 'source_identity_verified': True,
            'archive_sha256': archive_sha256,
            'version_url': f'{VEHICLE_SOURCE}/dataset/{VEHICLE_VERSION}',
            'source_class_names': [str(n) for n in raw], 'class_order': names, 'splits': counts,
            'staged_copy': source_label,
            'transformations': 'Source class names lower-cased at their original IDs; '
                               'annotations and source splits preserved without clipping; '
                               f"{counts.get('segmentation_lines_normalised', 0)} segmentation label "
                               'line(s) rewritten to their enclosing detection box.',
            'license': origin.get('license'),
        }, indent=2) + '\n', encoding='utf-8')
        staged.rename(destination)
    return prepared['names'], counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, epilog=(
        f'Download a YOLO26 export from {VEHICLE_SOURCE}/dataset/{VEHICLE_VERSION} into the '
        f'DataSet staging folder first; Roboflow requires sign-in.'))
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--archive', type=Path, help='Roboflow YOLO26 ZIP export inside DataSet.')
    inputs.add_argument('--export-dir', type=Path, help='Already unpacked YOLO export.')
    inputs.add_argument('--from-staging', action='store_true',
                        help='Use the newest official ZIP found in the DataSet staging folder.')
    parser.add_argument('--staging', type=Path, default=DEFAULT_STAGING,
                        help=f'DataSet staging folder (default: {DEFAULT_STAGING}).')
    parser.add_argument('--destination', type=Path, default=DESTINATION)
    args = parser.parse_args()

    if args.from_staging:
        archive = find_staged_archive(args.staging)
        if archive is None:
            raise SystemExit(
                f'No `{ARCHIVE_GLOB}` archive in {args.staging}. Download it from '
                f'{VEHICLE_SOURCE}/dataset/{VEHICLE_VERSION} into that folder, then rerun.')
        args.archive = archive

    if args.archive:
        if not args.archive.exists():
            raise SystemExit(f'Archive not found: {args.archive}. Copy it into {args.staging} first.')
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary).resolve()
            extract_archive(args.archive, folder)
            names, counts = prepare_export(
                folder, args.destination,
                archive_sha256=hashlib.sha256(args.archive.read_bytes()).hexdigest(),
                source_label=str(args.archive.resolve()))
    else:
        names, counts = prepare_export(args.export_dir, args.destination,
                                       source_label=str(args.export_dir.resolve()))
    print('Dataset reference:', VEHICLE_SOURCE)
    print('Class mapping:', dict(enumerate(names)))
    print('Validated splits:', counts)
    print('Course data:', args.destination)


if __name__ == '__main__':
    main()
