"""Author the English YOLO26 course and optional pretrained sentiment lesson."""
from build_course import BOOT, ROOT, md, code, notebook, write

import json
for existing in [ROOT/'02-object-detection/notebooks/01-yolo26-rock-paper-scissors.ipynb',
                 ROOT/'03-sentiment-analysis/pytorch/notebooks/04-pretrained-english-sentiment.ipynb']:
    if existing.exists() and any(c.get('execution_count') is not None for c in json.loads(existing.read_text(encoding='utf-8'))['cells']):
        raise RuntimeError('Executed notebooks already exist. Edit them in place to preserve saved outputs.')


notebook('02-object-detection/notebooks/01-yolo26-rock-paper-scissors.ipynb',[
    md('''# YOLO26: Rock, Paper, Scissors object detection

    **Learning outcomes:** distinguish classification and detection, inspect bounding-box
    labels, fine-tune YOLO26, evaluate held-out images, and display English predictions.

    This English edition uses Ultralytics YOLO26 instead of the original external
    PaddleYOLO workflow. Use the small `yolo26n.pt` model for the classroom. A pretrained
    COCO model does not know the three hand-gesture classes until it is fine-tuned.

    Prepare a **bounding-box detection** export, not a folder-only classification dataset.
    Prepare the official YOLO26 ZIP with `scripts/fetch_rps.py --archive <zip-path>`.
    The reference source is melikeavan/rock-paper-scissors-ishcs. The user archive has
    4,463 images with matching Roboflow v1 metadata; class IDs are visually verified as
    0=paper, 1=rock, 2=scissors. Original splits and annotations are preserved and recorded
    in provenance.json. Use RPS_DIRECTORY to isolate it from historical mirror data.
    '''),code(BOOT),code('''
    import json
    import warnings

    MODULE = COURSE / "02-object-detection"
    OUTPUT = MODULE / "outputs"
    # Keep Ultralytics settings local to this edition, before importing the package.
    os.environ["YOLO_CONFIG_DIR"] = str(OUTPUT / "ultralytics-config")
    import torch
    from ultralytics import YOLO, settings
    import ultralytics
    from ultralytics.utils import set_logging
    import matplotlib.pyplot as plt
    from detection_data import prepare_rps, RPS_DIRECTORY, RPS_SOURCE

    OUTPUT.mkdir(parents=True, exist_ok=True)
    SMOKE = os.environ.get("COURSE_SMOKE", "0") == "1"
    settings.update({"datasets_dir": str(MODULE / "data"),
                     "weights_dir": str(OUTPUT / "weights"),
                     "runs_dir": str(OUTPUT / "runs")})
    # Ultralytics redraws a per-iteration progress bar; inside a saved notebook every redraw
    # becomes a stored output record, so raise its log level and read the curve from results.png.
    set_logging(verbose=False)
    torch.set_num_threads(4)
    DEVICE = ("cuda" if torch.cuda.is_available()
              else "mps" if torch.backends.mps.is_available()
              else "cpu")

    # Ultralytics turns on warn-only determinism (seed plus torch.use_deterministic_algorithms).
    # On Apple Silicon the autograd kernel index_put_with_accumulate_mps has no deterministic
    # implementation, so that warning repeats once per epoch and buries the training log. It is
    # silenced here; the caveat stays real: on MPS a rerun matches in aggregate, not bit-for-bit.
    warnings.filterwarnings(
        "ignore",
        message="index_put_with_accumulate_mps does not have a deterministic implementation")
    print("Ultralytics version:", ultralytics.__version__)
    print("Device:", DEVICE)
    '''),md('''## 1. Validate the dataset and label mapping

    Each annotation row contains `class_id x_center y_center width height`. Coordinates
    are normalized by image width and height. Class IDs must agree with `data.yaml`.
    We lowercase English names but preserve their ID order. Training, validation, and
    test splits must be separate; the validator rejects identical images across splits.

    `COURSE_SMOKE=1` explicitly switches to COCO8 to test the YOLO26 software pipeline.
    That diagnostic run is not a Rock Paper Scissors experiment or its evaluation.
    '''),code('''
    if SMOKE:
        from detection_data import prepare_coco8
        DATA_CONFIG = str(prepare_coco8(MODULE / "data", OUTPUT / "coco8-smoke.yaml"))
        print("SMOKE TEST ONLY: COCO8 pipeline check; not hand-gesture training.")
    else:
        DATA_CONFIG = OUTPUT / "rps-data.yaml"
        config, counts = prepare_rps(MODULE / "data" / RPS_DIRECTORY, DATA_CONFIG)
        print("English class mapping:", dict(enumerate(config["names"])))
        print("Validated split sizes:", counts)
        DATA_CONFIG = str(DATA_CONFIG)
    '''),md('''## 2. Load pretrained weights and fine-tune

    YOLO26 supports training, validation, prediction, and export through the Ultralytics
    Python API. It also supports an end-to-end inference path. IoU, precision, recall,
    and mAP remain important; do not assume all historical YOLO post-processing details
    apply unchanged. See the linked official model guide for version-specific behavior.

    `workers=0` avoids notebook multiprocessing problems on Windows. The initial download
    needs internet. The smoke run uses a smaller image size and one epoch for speed. The
    classroom image size is 320 rather than 640: the historical mirror run at 640 pixels measured over
    twenty minutes per epoch on CPU, while on Apple silicon MPS a 320-pixel epoch measured about 114
    seconds. The cell
    ends by displaying `results.png` from the run folder, so loss and mAP are visible inline.
    '''),code('''
    weights = OUTPUT / "weights" / "yolo26n.pt"
    weights.parent.mkdir(parents=True, exist_ok=True)
    model = YOLO(str(weights))
    # Defaults are teaching parameters; runtime depends on the current dataset and hardware.
    # COURSE_EPOCHS shortens a pipeline check; the classroom default stays at ten epochs.
    EPOCHS = int(os.environ.get("COURSE_EPOCHS", 1 if SMOKE else 10))
    IMGSZ = 64 if SMOKE else 320
    print(f"Epochs: {EPOCHS}; image size: {IMGSZ}; smoke: {SMOKE}")
    # verbose=False keeps the saved notebook readable: the per-iteration progress bar added
    # about two thousand output records to the training cell without adding teaching value.
    results = model.train(data=DATA_CONFIG, epochs=EPOCHS, imgsz=IMGSZ,
                          batch=2 if SMOKE else 8, workers=0, device=DEVICE,
                          seed=42, deterministic=True, verbose=False,
                          project=str(OUTPUT / "runs"),
                          name="coco8-smoke" if SMOKE else "rps-ishcs-v1-yolo26n",
                          exist_ok=False, plots=True, cache=False)
    best = Path(model.trainer.best)
    if not best.exists():
        raise RuntimeError("Training did not produce a best checkpoint.")
    print("Saved checkpoint:", best.name)
    # Show the curves this run wrote into its own folder before reading the metrics table.
    curves = Path(model.trainer.save_dir) / "results.png"
    if curves.exists():
        figure, axis = plt.subplots(figsize=(12, 8))
        axis.imshow(plt.imread(curves))
        axis.axis("off")
        axis.set_title("Training curves from this run")
        plt.show()
    else:
        print("Expected plot not found:", curves)
    '''),md('''## 3. Validate the trained checkpoint

    Select model settings with validation data. Use the independent test split only after
    those decisions. COCO8 smoke mode has no separate test experiment, so it reports
    validation diagnostics only. mAP50 and mAP50-95 use different IoU criteria.
    '''),code('''
    trained = YOLO(str(best))
    split = "val" if SMOKE else "test"
    metrics = trained.val(data=DATA_CONFIG, split=split, device=DEVICE,
                          imgsz=IMGSZ, workers=0, batch=2 if SMOKE else 8,
                          project=str(OUTPUT / "runs"), name="evaluation")
    print(f"{split} mAP50: {metrics.box.map50:.4f}")
    print(f"{split} mAP50-95: {metrics.box.map:.4f}")
    report = {"smoke_test": SMOKE, "evaluation_split": split,
              "dataset": "COCO8" if SMOKE else RPS_DIRECTORY,
              "dataset_provenance": {} if SMOKE else json.loads((MODULE / "data" / RPS_DIRECTORY / "provenance.json").read_text(encoding="utf-8")),
              "map50": float(metrics.box.map50), "map50_95": float(metrics.box.map),
              "ultralytics_version": ultralytics.__version__}
    (OUTPUT / ("smoke-metrics.json" if SMOKE else "rps-metrics.json")).write_text(
        json.dumps(report, indent=2), encoding="utf-8")

    # The evaluation folder explains those numbers: a normalized confusion matrix and validation
    # crops with the predicted boxes drawn.
    for name in ("confusion_matrix_normalized.png", "val_batch0_pred.jpg"):
        figure_path = Path(metrics.save_dir) / name
        if figure_path.exists():
            figure, axis = plt.subplots(figsize=(10, 10))
            axis.imshow(plt.imread(figure_path))
            axis.axis("off")
            axis.set_title(f"{name} on the {split} split")
            plt.show()
        else:
            print("Expected plot not found:", figure_path)
    '''),md('## 4. Draw predictions with English labels'),code('''
    if SMOKE:
        from ultralytics.utils import ASSETS
        sample = ASSETS / "bus.jpg"
    else:
        directory = MODULE / "data" / RPS_DIRECTORY / "test" / "images"
        sample = next(p for p in directory.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    prediction = trained.predict(source=str(sample), conf=0.25, device=DEVICE,
                                  imgsz=IMGSZ, verbose=False)[0]
    for box in prediction.boxes:
        print(f"Class: {prediction.names[int(box.cls.item())]}; confidence: {float(box.conf.item()):.3f}")
    plt.figure(figsize=(8, 6))
    plt.imshow(prediction.plot()[:, :, ::-1])
    plt.title("YOLO26 detections" if not SMOKE else "COCO8 diagnostic predictions")
    plt.axis("off")
    plt.show()
    '''),md('''## Exercises and optional export

    Inspect missed objects and false positives. Compare two confidence thresholds without
    retraining. Compare nano and small models using the same splits. Inspect the exported
    dataset for near-duplicate photos or the same participant appearing across splits;
    exact-byte duplicate checks alone cannot detect all leakage.

    Export is optional: `trained.export(format="onnx")`. It may install additional export
    dependencies; first verify numerical agreement with the original model.

    Sources: [YOLO26](https://docs.ultralytics.com/models/yolo26/),
    [training API](https://docs.ultralytics.com/modes/train/),
    [requested Rock Paper Scissors project](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs).
    The official v1 export identity and processing are recorded in provenance.json.
    ''')])

notebook('03-sentiment-analysis/pytorch/notebooks/04-pretrained-english-sentiment.ipynb',[
    md('''# Optional: an already fine-tuned English sentiment model

    Use the PyTorch environment. This checkpoint was fine-tuned on SST-2; it is not an
    untrained classification head attached to a base language model. Its scores cannot
    be substituted for the IMDb LSTM experiment. The first run downloads model files.
    '''),code(BOOT),code('''
    from transformers import pipeline
    import torch
    model_id = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
    DEVICE = ("cuda" if torch.cuda.is_available()
              else "mps" if torch.backends.mps.is_available()
              else "cpu")
    classifier = pipeline("sentiment-analysis", model=model_id, device=DEVICE)
    reviews = ["The movie was engaging and beautifully acted.",
               "The story was dull and the ending made no sense."]
    for text, result in zip(reviews, classifier(reviews, truncation=True, max_length=512)):
        print(f"{result['label'].lower()} ({result['score']:.3f}): {text}")
    '''),md('''## Discuss

    What happens to a review longer than the model limit? How do movie-review and SST-2
    examples differ? Why can a high confidence score still be wrong?

    [Model card and provenance](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english).
    ''')])
