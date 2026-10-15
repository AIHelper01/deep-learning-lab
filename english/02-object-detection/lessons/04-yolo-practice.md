# Plan the detection experiment

1. Choose a versioned Rock Paper Scissors **detection** export and retain attribution.
2. Inspect representative images and bounding boxes. Use English class names.
3. Check separate train, validation, and test splits; avoid related frames across splits.
4. Run the notebook's class-ID, coordinate, and duplicate checks.
5. Fine-tune YOLO26n and examine the training curves and validation metrics.
6. Choose settings with validation results, then evaluate the held-out test split.
7. Inspect missed objects and false positives. Record dataset version, software version,
   seed, image size, epochs, hardware, and evaluation split alongside the checkpoint.

Changing the confidence threshold trades precision and recall. Increasing image size may
help small objects but requires more compute. More epochs can overfit. A detector trained
on clean single-hand images may struggle with multiple hands, occlusion, and new backgrounds.

Use the optional COCO8 smoke mode to check installation before obtaining the full export.
Label those results as a software diagnostic; they do not answer the hand-gesture task.

**Discussion:** how would you build a fair test set for a new instructor, camera, and room?

