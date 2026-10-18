"""Prepare the official melikeavan RPS v1 YOLO export; never substitute a mirror."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from zipfile import ZipFile
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'common'))
from detection_data import (RPS_WORKSPACE, RPS_PROJECT, RPS_DIRECTORY,
                            RPS_SOURCE, RPS_VERSION, prepare_rps)
DESTINATION = ROOT / '02-object-detection/data' / RPS_DIRECTORY


def prepare_export(source, destination=DESTINATION, class_names=None, archive_sha256=None):
    """Validate source identity and labels, then import to a fresh isolated directory."""
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if destination.exists():
        raise FileExistsError(f'Refusing to overwrite or merge an existing export: {destination}')
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Source and destination must be separate, non-nested directories.')
    config = yaml.safe_load((source / 'data.yaml').read_text(encoding='utf-8'))
    origin = config.get('roboflow', {})
    if (origin.get('workspace') != RPS_WORKSPACE or origin.get('project') != RPS_PROJECT
            or str(origin.get('version')) != str(RPS_VERSION)):
        raise ValueError(f'Export metadata must identify {RPS_SOURCE}/dataset/{RPS_VERSION}.')
    raw = config['names']
    if isinstance(raw, dict):
        raw = {int(k): v for k, v in raw.items()}
        if sorted(raw) != [0, 1, 2]:
            raise ValueError('Expected consecutive source class IDs 0, 1, 2.')
        raw = [raw[i] for i in range(3)]
    if len(raw) != 3:
        raise ValueError('Expected three source categories.')
    names = [str(n).strip().lower() for n in (class_names if class_names is not None else raw)]
    if len(names) != 3 or set(names) != {'rock', 'paper', 'scissors'}:
        raise ValueError('Inspect labeled samples, then pass --class-names with the verified '
                         'English names for IDs 0 1 2, in that order. No mapping is assumed.')
    config['names'] = names
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='rps-import-', dir=destination.parent) as temporary:
        staged = Path(temporary) / 'export'
        shutil.copytree(source, staged)
        (staged / 'data.yaml').write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
        prepared, counts = prepare_rps(staged, Path(temporary) / 'validated.yaml')
        for key in ('train', 'val', 'test'):
            config[key] = prepared[key]
        config['path'] = str(destination)
        (staged / 'data.yaml').write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
        (staged / 'provenance.json').write_text(json.dumps({
            'source': RPS_SOURCE, 'version': RPS_VERSION, 'source_identity_verified': True,
            'archive_sha256': archive_sha256,
            'version_url': f'{RPS_SOURCE}/dataset/{RPS_VERSION}',
            'source_class_names': [str(n) for n in raw], 'class_order': names, 'splits': counts,
            'transformations': 'Verified semantic names assigned at original IDs; '
                               'annotations and source splits preserved without clipping.',
            'license': origin.get('license'),
        }, indent=2) + '\n', encoding='utf-8')
        staged.rename(destination)
    return prepared['names'], counts


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog=(
        f'Download a YOLO export from {RPS_SOURCE}/dataset/{RPS_VERSION} first. '
        'Roboflow may require sign-in; numeric gesture labels must be visually verified.'))
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--archive', type=Path, help='Official Roboflow YOLO26 ZIP export.')
    inputs.add_argument('--export-dir', type=Path, help='Unpacked official YOLO export.')
    parser.add_argument('--class-names', nargs=3, metavar=('ID0', 'ID1', 'ID2'),
                        help='Verified names rock/paper/scissors in original numeric ID order.')
    args = parser.parse_args()
    if args.archive:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary).resolve()
            with ZipFile(args.archive) as zipped:
                for item in zipped.infolist():
                    if not (folder / item.filename).resolve().is_relative_to(folder):
                        raise ValueError('Unsafe archive path.')
                zipped.extractall(folder)
            names, counts = prepare_export(folder, class_names=args.class_names,
                archive_sha256=hashlib.sha256(args.archive.read_bytes()).hexdigest())
    else:
        names, counts = prepare_export(args.export_dir, class_names=args.class_names)
    print('Dataset reference:', RPS_SOURCE)
    print('Class mapping:', dict(enumerate(names)))
    print('Validated splits:', counts)
    print('Course data:', DESTINATION)


if __name__ == '__main__':
    main()
