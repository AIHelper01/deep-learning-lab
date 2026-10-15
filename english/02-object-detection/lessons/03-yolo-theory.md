# Detection concepts and YOLO26

A bounding box can be described by corners or by center, width, and height. YOLO text
annotations use normalized center coordinates and size. The class ID refers to the
class-name order in the dataset configuration; changing this order changes label meaning.

Intersection over Union is `intersection area / union area`. A high confidence score is
not the same as accurate localization. Precision measures how many predicted objects are
correct; recall measures how many labeled objects are found. Average precision summarizes
the precision-recall curve. mAP averages over classes, with a stated IoU criterion.

Traditional NMS removes lower-scoring overlapping predictions. YOLO26 supports an
end-to-end inference path as well as version-specific detection options. Teach NMS as a
general detection concept and consult the installed version's documentation rather than
assuming every YOLO model requires the same post-processing.

The backbone extracts features, the neck combines scales, and the head predicts objects.
The pretrained COCO checkpoint knows COCO categories. Fine-tuning adapts it to the three
English hand-gesture classes. A small model is a useful classroom starting point; model
size alone does not repair bad annotations or train/test leakage.

Source: [Ultralytics YOLO26 model guide](https://docs.ultralytics.com/models/yolo26/).

