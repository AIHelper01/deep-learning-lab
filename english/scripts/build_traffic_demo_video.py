"""Compose a short synthetic traffic clip from real dataset vehicle crops.

Public sample traffic videos are not bundled with the course and Roboflow only ships images,
so the tracking lesson needs a clip it can build offline. Real vehicle crops taken from the
dataset annotations are composited onto a generated two-lane road. Every sprite is spawned
exactly once and crosses the counting line exactly once, which gives the notebook a ground
truth to compare the tracker against instead of a guess.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import cv2
import numpy as np
import yaml

FRAME_SIZE = (640, 640)


def collect_crops(export_dir: Path, classes: list[str], per_class: int = 4) -> dict[str, list[np.ndarray]]:
    """Crop annotated vehicles out of the validation split, keeping a size range for variety."""
    images = sorted((export_dir / 'valid' / 'images').glob('*.jpg'))
    crops: dict[str, list[np.ndarray]] = {name: [] for name in classes}
    for image_path in images:
        if all(len(values) >= per_class for values in crops.values()):
            break
        label = export_dir / 'valid' / 'labels' / (image_path.stem + '.txt')
        if not label.exists():
            continue
        image = cv2.imread(str(image_path))
        if image is None:
            continue
        height, width = image.shape[:2]
        for line in label.read_text(encoding='utf-8').splitlines():
            fields = line.split()
            if len(fields) != 5:
                continue
            class_id = int(fields[0])
            if class_id >= len(classes):
                continue
            name = classes[class_id]
            if len(crops[name]) >= per_class:
                continue
            x, y, box_w, box_h = map(float, fields[1:])
            left = max(0, int((x - box_w / 2) * width)); right = min(width, int((x + box_w / 2) * width))
            top = max(0, int((y - box_h / 2) * height)); bottom = min(height, int((y + box_h / 2) * height))
            if right - left < 60 or bottom - top < 30:
                continue  # Too small to composite without obvious blur.
            crop = image[top:bottom, left:right]
            crops[name].append(cv2.resize(crop, (120, int(120 * crop.shape[0] / crop.shape[1]))))
    return {name: values for name, values in crops.items() if values}


def draw_background(lane_offset: int) -> np.ndarray:
    """Draw a fixed two-lane road; only the centre dashes move, giving parallax-free motion."""
    canvas = np.full((*FRAME_SIZE[::-1], 3), 60, dtype=np.uint8)
    canvas[:, :, 1] = 70  # Asphalt with a slight green tint.
    canvas[0:110, :] = (90, 120, 90)      # Far verge.
    canvas[530:640, :] = (90, 120, 90)    # Near verge.
    canvas[110:530, 0:30] = (40, 40, 200)
    canvas[110:530, 610:640] = (40, 40, 200)
    for y in range(-lane_offset, FRAME_SIZE[1], 80):
        cv2.rectangle(canvas, (315, y), (325, y + 44), (230, 230, 230), -1)
    return canvas


def build(export_dir: Path, output: Path, *, fps: int = 12, frames: int = 108,
          seed: int = 7) -> dict:
    """Render the clip and return the ground-truth spawn record."""
    import sys
    sys.path.insert(0, str(export_dir))
    classes = yaml.safe_load((export_dir / 'data.yaml').read_text(encoding='utf-8'))['names']
    crops = collect_crops(export_dir, classes)
    rng = random.Random(seed)
    rng_b = np.random.default_rng(seed)

    # Every spawn crosses the counting line once. Near-lane vehicles travel down-frame,
    # far-lane vehicles travel up-frame, so both counting directions get exercised.
    spawns = []
    lane_plan = [('forward', 120), ('forward', 430), ('backward', 210), ('backward', 520)]
    for index in range(6):
        direction, lane_x = lane_plan[index % 4]
        name = rng.choice(sorted(crops))
        start = rng.randint(0, max(1, frames - 50))
        spawns.append({'id': index, 'class': name, 'direction': direction,
                       'lane_x': lane_x, 'start_frame': start})

    counter = {name: 0 for name in classes}
    writer = cv2.VideoWriter(str(output), cv2.VideoWriter_fourcc(*'mp4v'), fps, FRAME_SIZE)
    if not writer.isOpened():
        raise RuntimeError(f'OpenCV could not open {output} for writing.')
    for frame_index in range(frames):
        canvas = draw_background((frame_index * 9) % 80)
        for spawn in spawns:
            progress = (frame_index - spawn['start_frame']) / 48
            if not 0 <= progress <= 1:
                continue
            scale = 0.45 + 0.9 * progress if spawn['direction'] == 'forward' else 1.35 - 0.9 * progress
            y_center = 60 + 520 * progress if spawn['direction'] == 'forward' else 580 - 520 * progress
            for crop in crops[spawn['class']]:
                width = max(28, int(crop.shape[1] * scale))
                height = max(14, int(crop.shape[0] * scale))
                resized = cv2.resize(crop, (width, height))
                top, left = int(y_center - height / 2), int(spawn['lane_x'] - width / 2)
                x1, y1 = max(0, left), max(0, top)
                x2, y2 = min(FRAME_SIZE[0], left + width), min(FRAME_SIZE[1], top + height)
                if x2 <= x1 or y2 <= y1:
                    continue
                region = canvas[y1:y2, x1:x2]
                patch = resized[y1 - top:y2 - top, x1 - left:x2 - left]
                if patch.shape[:2] != region.shape[:2]:
                    continue
                canvas[y1:y2, x1:x2] = patch
                break
        cv2.line(canvas, (0, 320), (640, 320), (0, 255, 255), 2)
        cv2.putText(canvas, f'frame {frame_index:03d}', (12, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2)
        writer.write(canvas)
    writer.release()
    for spawn in spawns:
        counter[spawn['class']] += 1
    ground_truth = {'video': str(output), 'fps': fps, 'frames': frames,
                    'counting_line': [0, 320, 640, 320],
                    'spawns': spawns, 'expected_vehicles_per_class': counter,
                    'expected_total_crossings': len(spawns),
                    'note': 'Each spawned vehicle is drawn once and crosses the line once.'}
    output.with_suffix('.ground-truth.json').write_text(json.dumps(ground_truth, indent=2),
                                                        encoding='utf-8')
    return ground_truth


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fps', type=int, default=12)
    parser.add_argument('--frames', type=int, default=108)
    parser.add_argument('--seed', type=int, default=7)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    truth = build(args.export_dir, args.output, fps=args.fps, frames=args.frames, seed=args.seed)
    print('Video:', truth['video'])
    print('Expected crossings:', truth['expected_total_crossings'], truth['expected_vehicles_per_class'])


if __name__ == '__main__':
    main()
