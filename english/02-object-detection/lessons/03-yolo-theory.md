# Detection concepts and YOLO26

This course uses Ultralytics YOLO26n. A detection model outputs where objects are, what class each one has, and a
confidence score, which is a different supervision target from one label per image.

## Learning goals

- The input is an image and the supervision is a set of boxes plus classes. YOLO text annotations use
  `class_id xc yc w h`, with the geometry normalised by image width and height. A box may also be written as two
  corners, so always check which convention a file uses.
- A backbone plus multi-scale feature fusion supports objects of very different sizes; the head learns position and
  class. The exact YOLO26 block layout follows the [official YOLO26 documentation](https://docs.ultralytics.com/models/yolo26/),
  not a diagram of an older release.
- YOLO26 offers an end-to-end inference path, so do not transplant the post-processing details of another YOLO version
  without checking. This course reports the boxes and scores the installed API actually returns.
- Intersection over Union is `intersection area / union area`, so a high confidence score is not the same thing as an
  accurately placed box. Precision counts how many predictions are correct, recall counts how many labeled objects were
  found, and average precision summarises the precision-recall curve. mAP averages over classes under a stated IoU
  criterion, so mAP50 and mAP50-95 answer different questions and are not interchangeable numbers.
- Train on the training split, choose settings on validation, and report the held-out test split only once. The
  pretrained COCO classes are not the rock-paper-scissors classes, which is exactly why fine-tuning is needed.

## Conventions of this lab

We use the original 3,939/338/186 train/validation/test split of
[Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1), the model
`yolo26n.pt`, and the original ids `0=paper, 1=rock, 2=scissors`; `n` denotes the nano model scale chosen here. Record
the framework, dataset version and random seed together with any result.

Continue to [the practice lesson](04-yolo-practice.md); the second case in this module,
[vehicle counting and traffic flow](../notebooks/02-yolo26-vehicle-counting.ipynb), adds counting and line crossings on
top of the same detection output. Format conversion and the viewer are a
[separate topic](../dataset-formats/README.md) and are not re-implemented here.

The superseded lecture survives only in the Chinese course
[archive](../../../02-object-detection/archive/lessons/03-yolo-theory.md); its historical architecture notes do not
describe the model that was actually run here.
