# assets

- `01_Titanic-Case-<N>.png`: the figures produced by the verified English-side run, exported by
  `scripts/embed_expected_outputs.py` and referenced from the notebook through `../assets/`.
- `reference-1.png`: screenshot of the interactive classification-threshold and confusion-matrix tool
  (TP/FP/FN/TN update as the threshold moves to 0.50), referenced by the model-evaluation section.
- `reference-2.png` / `reference-3.png`: screenshots of the interactive linear-regression
  gradient-descent tool (Weight/Bias sliders plus learning rate and Start/Step/Reset controls),
  referenced by the hyperparameter and learning-rate sections.
- The three `reference-*` images come from interactive teaching tools (see the `w-interactive-demo`
  tool set). The notebook prose refers to them but does not embed them, so they stay as handout
  material. Name new images `<name>-<N>.<ext>` (`scripts/check_docs_assets.py` enforces this).
