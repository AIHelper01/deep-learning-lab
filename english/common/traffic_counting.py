"""Count vehicles in images and in tracked video frames for the traffic-counting lesson.

Detection alone answers "how many vehicles are visible in this picture". Traffic flow answers
"how many distinct vehicles passed a line over time", which needs a stable tracker ID per
vehicle plus a crossing test. These helpers are deliberately small and dependency-free so the
notebook can show every step.
"""
from collections import Counter, defaultdict
from pathlib import Path

VEHICLE_CLASSES = ('truck', 'bicycle', 'bus', 'car', 'motorcycle')


def ground_truth_counts(image, names):
    """Return the ``{class name: count}`` annotation tally for one YOLO image.

    A YOLO export keeps ``images/`` and ``labels/`` as sibling folders, so the label is
    looked up there first; the file beside the image is only a flat-layout fallback.
    """
    image = Path(image)
    candidates = (image.parent.parent / 'labels' / (image.stem + '.txt'),
                  image.with_name(image.stem + '.txt'))
    counter = Counter()
    for path in candidates:
        if not path.is_file():
            continue
        for line in path.read_text(encoding='utf-8').splitlines():
            fields = line.split()
            if len(fields) >= 5 and fields[0].lstrip('-').isdigit():
                counter[str(names[int(fields[0])])] += 1
        break
    return dict(counter)


def tally_predictions(boxes, names, vehicle_classes=VEHICLE_CLASSES):
    """Return per-class counts and the total for one detected image.

    Only configured vehicle classes are tallied, so a model that also knows pedestrians or
    traffic signs cannot inflate a traffic figure.
    """
    detected = {str(names[int(cls)]).strip().lower() for cls in boxes.cls.tolist()}
    unused = sorted(detected - set(vehicle_classes))
    counter = Counter()
    for cls, confidence in zip(boxes.cls.tolist(), boxes.conf.tolist()):
        label = str(names[int(cls)]).strip().lower()
        if label in vehicle_classes:
            counter[label] += 1
    return {'per_class': dict(counter), 'total': sum(counter.values()),
            'non_vehicle_classes_detected': unused}


def side(point, line):
    """Signed side of a point relative to the segment ``((x0, y0), (x1, y1))``."""
    (x0, y0), (x1, y1) = line
    return (x1 - x0) * (point[1] - y0) - (y1 - y0) * (point[0] - x0)


class LineCrossingCounter:
    """Count each tracked vehicle the first time its anchor crosses a counting line.

    The anchor is the bottom-centre of the box, i.e. where the vehicle touches the road, which
    behaves better than the box centre on perspective views. A track counts once per direction,
    and reversing back across the line does not double count.
    """

    def __init__(self, line, vehicle_classes=VEHICLE_CLASSES):
        self.line = line
        self.vehicle_classes = set(vehicle_classes)
        self.previous = {}
        self.counted = {}
        self.per_class = defaultdict(Counter)
        self.last_event = {}
        self.direction_names = {+1: 'forward', -1: 'backward'}

    def update(self, frame_index, timestamp, boxes, names):
        """Feed one tracked frame and return the counts produced so far."""
        for box in boxes:
            if box.id is None:
                continue  # Untracked detections have no stable identity to deduplicate on.
            cls, confidence, track_id = int(box.cls.item()), float(box.conf.item()), int(box.id.item())
            label = str(names[cls]).strip().lower()
            if label not in self.vehicle_classes:
                continue
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            anchor = ((x1 + x2) / 2, y2)
            value = side(anchor, self.line)
            previous = self.previous.get(track_id)
            self.previous[track_id] = value
            if self.counted.get(track_id) is not None or previous is None:
                continue
            if (previous > 0) != (value > 0):
                direction = 1 if value > 0 else -1
                self.counted[track_id] = direction
                self.per_class[direction][label] += 1
                self.last_event[direction] = {'class': label, 'track_id': track_id,
                                              'frame': frame_index, 'timestamp': timestamp}
        return self.summary()

    def summary(self):
        """Return direction totals, per-class breakdowns and the unique vehicle count."""
        result = {}
        for direction, label in self.direction_names.items():
            classes = {k: v for k, v in self.per_class[direction].items()}
            result[label] = {'crossings': sum(classes.values()), 'per_class': classes}
        for direction, label in self.direction_names.items():
            if direction in self.last_event:
                result[label]['last_crossing'] = self.last_event[direction]
        result['unique_vehicles_seen'] = len(self.counted)
        result['tracks_observed'] = len(self.previous)
        return result

    def vehicles_per_minute(self, fps, total_frames):
        """Convert crossings into a flow rate using the video's own frame rate."""
        duration_minutes = total_frames / fps / 60 if fps else 0
        total = sum(sum(self.per_class[d].values()) for d in self.direction_names)
        return {'duration_seconds': round(total_frames / fps, 2) if fps else None,
                'total_crossings': total,
                'vehicles_per_minute': round(total / duration_minutes, 1) if duration_minutes else None}

def count_video(model, video, line, *, conf=0.25, imgsz=416, device='cpu', tracker='bytetrack.yaml',
                vehicle_classes=VEHICLE_CLASSES, annotated_frames=(0, 40, 80)):
    """Track one video and return line-crossing traffic counts plus a few annotated frames.

    The model may be a COCO pretrained or a course fine-tuned checkpoint; the tally always
    keeps only the configured vehicle classes. Annotated frames are returned as RGB arrays so
    a notebook can display them without a second pass over the video.
    """
    import cv2

    capture = cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise RuntimeError(f'OpenCV could not open the video: {video}')
    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    width, height = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    declared_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    capture.release()
    wanted = {index for index in annotated_frames}
    counter = LineCrossingCounter(line, vehicle_classes=vehicle_classes)
    frames_read = 0
    samples = []
    # One streaming tracking pass: persist=True keeps tracker IDs across frames.
    for frame_index, result in enumerate(model.track(source=str(video), stream=True, persist=True,
                                                     conf=conf, imgsz=imgsz, device=device,
                                                     tracker=tracker, verbose=False)):
        counter.update(frame_index, frame_index / fps, result.boxes, result.names)
        if frame_index in wanted:
            samples.append({'frame': frame_index, 'rgb': result.plot()[:, :, ::-1].copy()})
        frames_read += 1
    summary = counter.summary()
    summary.update({'video': str(video), 'fps': round(fps, 2), 'frames_analysed': frames_read,
                    'declared_frames': declared_frames, 'frame_size': [width, height],
                    'counting_line': list(line)})
    summary['flow'] = counter.vehicles_per_minute(fps, frames_read)
    return summary, samples
