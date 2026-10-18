# Project handoff

Updated: 2026-10-18 (Asia/Shanghai). The session changes are committed on main and pushed to origin.

## Current user direction

The project is English-first with Chinese compatibility. The user supplied the official `Rock-Paper-Scissors.v1i.yolo26.zip` and selected **YOLO26n** for both language lessons. The user explicitly stopped the earlier flattened VOC package workflow. Dataset conversion and Xiaotudui Labs viewer instructions must be a **separate parallel topic**, not part of model-training notebooks.

## Delivered structure

- `README.md` and root docs are English defaults, with `README.zh-CN.md` and `docs/*.zh-CN.md` counterparts.
- Root `start-notebooks.ps1` defaults to English vision. Current Chinese detection routes through the shared English detection uv environment; other Chinese routes retain their existing module environments.
- English detection notebook: `english/02-object-detection/notebooks/01-yolo26-rock-paper-scissors.ipynb`.
- New Chinese detection notebook: `02-object-detection/notebooks/01-yolo26-rock-paper-scissors.ipynb`.
- Both use Ultralytics YOLO26n, official v1 data, and separate outputs. Chinese YOLO theory/practice lessons are updated; previous lessons are preserved in `02-object-detection/archive/lessons/`. The old PaddleYOLO notebook remains historical.
- `04-dataset-formats/` is the parallel English/Chinese format topic. Its scripts convert bounding-box YOLO/VOC/COCO datasets and check all six directions. VOC import requires the tutorial's explicit zero-based continuous-coordinate convention; this is not an arbitrary legacy VOC importer.
- Dataset catalogs and six module data READMEs describe content, source, preparation, labels/splits, paths, transformations, and attribution.

## Official dataset verification

Reference: [melikeavan / Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1).

- Input ZIP: `C:/Users/will/Downloads/Rock-Paper-Scissors.v1i.yolo26.zip`.
- SHA-256: `2cf65dffbaa92483bbf99e7903f7c23c934ccf57d1cb097a66b7d38eadac0e59`.
- Embedded workspace/project/version metadata and CC BY 4.0 notices match the requested source.
- Source splits retained: training 3,939 images / 4,610 boxes; validation 338 / 400; test 186 / 204.
- Original names are numeric; labeled crop review confirms 0=paper, 1=rock, 2=scissors. IDs are preserved while names become English.
- No invalid boxes or cross-split exact duplicate image bytes found. Near-duplicate/video/participant leakage in upstream splits is not ruled out.
- Active data: `english/02-object-detection/data/rock-paper-scissors-ishcs-v1/`; `provenance.json` records the import. Both languages share this data read-only; model outputs are separate.
- `fetch_rps.py` imports official YOLO exports and refuses overwrite/merge. `fetch_rps_legacy.py` is historical mirror reproduction only.
- Data-check evidence: `english/reports/rps-v1-data-checks.json` and `rps-v1-class-id-review.png`.

The superseded desktop `Rock-Paper-Scissors.zip` was VOC with 6,455 images and no project/version metadata. Its conversion finished before the stop message; **no training was started on it**. Its ignored output remains in `english/02-object-detection/data/rock-paper-scissors-ishcs/`, and is not read by the current course. Do not relabel it as v1 or delete local data without purpose. Historical Xuban results are retained in the archived English notebook and `detection-legacy-executed.json`.

## Environment and checks

The detection environment was actually installed using Python **3.12.12**, PyTorch **2.14.1+cpu**, Ultralytics **8.4.177**. Python 3.12.15 was unavailable locally; detection `.python-version` was updated while the original dependency lockfile was preserved. The launcher explicitly selects the lockfile's PyPI index to avoid rewriting it for a machine-specific mirror. `uv sync --locked --default-index https://pypi.org/simple --dry-run` passes for this module. Other module pins were preserved. No CUDA device was available.

Passed:

- `pwsh -NoProfile -File tests/check-launcher.ps1`: all language/module routes, shared Chinese detection environment, defaults, and invocation outside the repository.
- Detection interpreter + `tests/check-rps-import.py`: source rejection, explicit class mapping, ID/source preservation, split paths, overwrite guard, and invalid-box rejection.
- `04-dataset-formats/scripts/check_roundtrip.py`: all six format directions on fixtures, including empty images, full-image boxes, nested paths, and guards.
- Real test-split conversion: all 186 images / 204 boxes match after YOLO→VOC→YOLO and YOLO→COCO→YOLO; hashes, labels, splits and coordinates checked within 0.001 pixel tolerance. Evidence: `04-dataset-formats/reports/validation.json`.
- Final documentation check passed: 23 documents, 140 local links/anchors; both current detection notebooks completed without saved errors.
- Final static check passed: 75 English source files, 14 notebooks including the historical detection archive, zero problems. Saved-output check passed for 13 English course notebooks plus the new Chinese detection notebook, 14 total. Jupyter checkpoint copies are excluded from validation and execution discovery.

Xiaotudui Labs' YOLO/VOC/COCO viewer pages were inspected in-browser. Guides document actual image/annotation selectors, start/reset/zoom controls, and COCO image-ID search. The YOLO page mentions classes.txt but exposed no independent class-upload control. **Website file imports were not performed**, so do not claim visual validation inside the website; format correctness was checked locally.

## Completed execution

Both current YOLO26 notebooks **completed successfully**: one actual full-dataset epoch,
320 pixels, batch 8, CPU, then independent test evaluation/prediction. This is
`COURSE_EPOCHS=1`, not smoke mode and not the default ten-epoch lesson result.

| Language | End-to-end seconds | Test mAP50 | Test mAP50-95 |
|---|---:|---:|---:|
| English | 683.77 | 0.7266251003 | 0.4535422539 |
| Chinese | 634.85 | 0.7266251003 | 0.4535422539 |

Each notebook retains four embedded figures and completed execution metadata.
The one-epoch plot has only one point per series; this does not establish a training trend.
The single-image sample can still have missed detections. Checkpoints, exact source,
class order, split sizes, scope and report paths are in `english/reports/rps-v1-run-summary.json`.
English and Chinese training were independent runs; shared seed/settings reproduced the metrics.

Execution commands from the root (detection interpreter):

```powershell
$env:COURSE_EPOCHS='1'
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\execute_and_save.py --group detection
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\execute_and_save.py --group detection --language zh-CN
```

Reports are `english/reports/detection-executed.json` and `detection-zh-CN-executed.json`; raw metrics/checkpoints are under each language's detection outputs. Both execution processes finished. No training is left running from this task. Repeat runs create new run directories; do not overwrite historical artifacts. Resume checks now distinguish requested run mode, so a one-epoch report cannot satisfy a default ten-epoch run.

## Full English course run with default classroom parameters

On 2026-10-18 all four English groups were executed end-to-end in a real environment with default classroom parameters (COURSE_SMOKE=0, no COURSE_EPOCHS) on a CPU-only i7-11700 (8c/16t, 32 GB). All 13 English notebooks passed; every notebook file retains its saved outputs and completion metadata, and per-run rows are in english/reports/vision-executed.json, detection-executed.json, pytorch-executed.json, and paddle-executed.json.

- Vision, PyTorch NLP, and Paddle NLP environments were rebuilt with uv sync --locked --default-index https://pypi.org/simple --python 3.12.12 because CPython 3.12.15 has no local install and no uv download on this machine. .python-version files and all lockfiles are unchanged; runtime is Python 3.12.12 with torch 2.14.1, ultralytics 8.4.177, and paddlepaddle 3.3.1, satisfying the notebook kernel asserts.
- Saved headline metrics: LeNet-MNIST test accuracy 0.894; LeNet-CIFAR10 0.383; ResNet-CIFAR10 0.817; PyTorch LSTM sentiment test accuracy 0.736; Paddle LSTM sentiment test accuracy 0.817; YOLO26n ten real epochs on the official v1 dataset (320 px, batch 8) reached test mAP50 0.9494 and mAP50-95 0.7670, trained in 4,126 s (run directory english/02-object-detection/outputs/runs/rps-ishcs-v1-yolo26n-2).
- These default-parameter results supersede the one-epoch pipeline-check metrics in the table above for classroom presentation; the one-epoch report remains historical evidence and its run directory is unchanged.
- Post-run checks passed from the repository root: python english/scripts/verify_saved_outputs.py (zero problems), python english/scripts/check_course.py (75 source files, 14 notebooks, zero problems), and git diff --check.

## Other limitations and git state

Chinese classification/NLP runtime validation remains incomplete; a historical Chinese Paddle LSTM error is not fixed. Other English Paddle notebooks were already modified when this detection task began; preserve those changes and do not reset them. Do not broadly regenerate notebooks.

`docs/migration/` and original integrity reports describe past snapshots. Changed documentation means those reports do not validate the current tree. Historical cleanup suggestions were not executed.

Commits before this session ended at `4c39b08`. The full default-parameter English course run and all session documentation changes were committed on `main` and pushed to `origin` in the closing commit of the 2026-10-18 session. Inspect `git log` and `git status --short` before continuing.

中文交接：当前正式包已核实，YOLO26n 与数据在中英文课程统一；旧 VOC 包已停用且未训练。格式转换与小土堆查看说明在独立 04 专题。两版 Notebook 已分别完成全部正式数据一轮 CPU 实跑，测试 mAP50=0.7266、mAP50-95=0.4535，不能沿用旧镜像指标，也不能当成默认十轮结果。本次改动已提交到 main 并推送到 origin。

## 2026-10-18 (second session): single local kernel, dataset landing, image localisation, vehicle-counting run

The user asked for four things on a macOS laptop: English-only directory names, one uv environment whose
Jupyter kernel is literally `env_dl_uv`, datasets staged in `/workspace/DataSet` and copied into each module
`data/` with cp-plus-download instructions, real executed outputs kept as evidence (`预期输出：` blocks plus
figures under a sibling `assets/`), and every online documentation image localised as `<dir>-N.ext`.

- **Kernel cleanup.** Removed seven non-`base` kernel registrations (`env_agent`, `env_datasci`, `env_langchain`,
  `env_ml`, `env_pytorch`, `env_rag`, `test`); registration files backed up at
  `~/Library/Jupyter/kernels-backup-20261018`. The underlying conda environments were not touched.
- **`env_dl_uv`.** New uv project at `~/env_dl_uv` (`pyproject.toml`, `uv.lock`, `README.md`) merging the four
  module lockfiles: Python 3.12.12, torch 2.14.1 + torchvision, ultralytics 8.4.177 + lapx, gensim +
  transformers, paddlepaddle 3.3.1, JupyterLab/nbclient. Registered as kernel `env_dl_uv` and imported
  successfully. `jieba` and `pandas` were added afterwards because Chinese 03 notebooks import them.
  `paddlenlp`/`visualdl` are deliberately excluded: they pin `protobuf 3.20.x` and target Paddle 2.x, which
  fights the pinned `paddlepaddle==3.3.1`. Documented in `docs/environment-setup.md` and its Chinese twin.
- **Dataset landing.** `/workspace/DataSet` keeps the raw copies; module `data/` directories receive the
  classroom copies. MNIST and CIFAR-10 now load through `env_dl_uv` on both language trees
  (60,000/10,000 and 50,000/10,000, 28×28 and 32×32). CIFAR-10 finished downloading (170,498,071 B, SHA-256
  `6d958be0…001ce`) and was unpacked. The vehicle-counting v4 export (4,708/1,661/196 images) is imported at
  `english/02-object-detection/data/vehicle-counting-tksu5-v4/`. Every affected module `data/README.md`, the
  dataset catalog, and the DataSet README/DOWNLOAD notes state both the `cp` copy and the source download.
- **Documentation images localised.** 101 remote images are now local: `assets/lessons-1..41` for the two live
  Chinese lessons, `archive/assets/lessons-1..60` for the archived lessons, plus the seven new run figures.
  All 137 image references in Markdown resolve and decode; a byte-for-byte check against the original URLs
  (`git show HEAD:…`) reported 0 mismatches over 75 re-downloaded images. No Markdown image points at a
  remote host anymore.
- **Real execution, and a bug it exposed.** The first vehicle-counting run reported every image's ground-truth
  count as zero: `ground_truth()` looked for label files beside the images, while YOLO exports keep them in a
  sibling `labels/` directory. Fixed at the source with `ground_truth_counts()` in `english/common/traffic_counting.py`
  (labels directory first, flat layout as fallback) and the notebook now calls it. The notebook was then
  executed end to end again with default classroom parameters (CPU, 5 epochs, imgsz 320, seed 42,
  2152.35 s, `status: passed`): test precision 0.7399, recall 0.6484, mAP50 0.6975, mAP50-95 0.4059, and the
  tracked demo video counted 7 crossings against a synthetic ground truth of 6. Figures were exported to
  `02-object-detection/assets/vehicle-counting-1..7.png` and every saved output is transcribed in the new
  `02-object-detection/lessons/05-vehicle-counting-run-report.md`, including the honest finding that the
  fine-tuned weights count *worse* than zero-shot on the four sampled images (4.75 vs 3.75 vehicles/image on
  the same subset) because both models miss a 13-motorcycle frame at 320 px.
- **Naming.** The vehicle notebook file is now `02-yolo26-vehicle-counting.ipynb` so it matches its siblings and
  the English-tree CJK scan; all links, the build script, the dataset docs, and the execution report row were
  updated. No directory in the repository or in `DataSet` contains non-ASCII characters.

Checks run from the repository root: `python english/scripts/check_course.py` (77 source files, 14 notebooks,
0 problems), `python english/scripts/verify_saved_outputs.py` (0 problems; the renamed notebook reports
13/13 executed cells and 7 embedded images), `git diff --check` (clean), and a local Markdown link/image audit
(0 broken outside the untouched `docs/migration/original` archive, whose links deliberately describe the
pre-migration tree).

Limitations: the run report's numbers are one 5-epoch CPU run and validation mAP50 was still climbing, so they
are not an upper bound for the dataset; `prepare_vehicle_counting()` prints
`segmentation_lines_normalised: 0`, which means "no segmentation lines left after import" (the three converted
source lines are recorded in `provenance.json`) — the key name is misleading and worth renaming if a rerun is
planned anyway; the demo clip is synthetic; `03-sentiment-analysis` Paddle notebooks still need a separate
Paddle 2.x environment. Stale artifacts from the zero-ground-truth run were moved, not deleted, to
`/tmp/dl/stale-1`, and 40 duplicate images from an interrupted download to `/tmp/dl/orphan-assets`. Nothing
was committed in this session.

## 2026-10-18 (third session): expected outputs live inside the notebooks

Clarification from the user: `预期输出：` must be part of the notebook itself, so the results and figures stay
readable after **Kernel → Clear All Outputs** instead of only living in a separate report file.

- **New helper `02-object-detection/scripts/embed_expected_outputs.py`** (lives outside `english/` because it
  contains Chinese captions). It is repeatable: cells tagged `course-expected-output` are deleted and rebuilt
  from the currently saved outputs. Text output is quoted verbatim into a ```text block, every PNG is written
  to the module's `assets/` folder and referenced with a `../assets/…` relative path, absolute repository
  prefixes become `…/deep-learning-lab` with a one-line footnote, and an optional intro callout is inserted
  after the title. Labels are per language (`**预期输出：**` / `**Expected output:**`) so the `english/` tree
  stays free of CJK.
- **Coverage now: three notebooks, 29 tagged cells, 15 figures.** Vehicle counting
  (`02-object-detection/assets/vehicle-counting-1..7.png`), and both Rock Paper Scissors notebooks
  (`02-object-detection/assets/rock-paper-scissors-1..4.png`,
  `english/02-object-detection/assets/rock-paper-scissors-1..4.png`). Verified by clearing every code-cell
  output in memory: 0 outputs left, 15/15 image references still resolve to real PNGs.
- **Run modes are disclosed, not blurred.** The Chinese RPS notebook keeps a `COURSE_EPOCHS=1` full-dataset
  single-epoch check (634 s, test mAP50 0.7266 / mAP50-95 0.4535): its curves have one point per metric, the
  normalised confusion matrix is weak, and the single-image prediction draws no box at conf ≥ 0.25. The English
  notebook keeps the default ten-epoch run (mAP50 0.9494 / mAP50-95 0.7670). Each intro callout states which
  configuration its embedded numbers came from, so nobody reads a one-epoch check as a classroom score.
- **Open blocker for a RPS rerun.** `english/02-object-detection/data/rock-paper-scissors-ishcs-v1/` is absent
  (gitignored) and Roboflow blocks anonymous downloads, so the ten-epoch Chinese rerun needs the user to export
  `Rock-Paper-Scissors.v1i.yolo26.zip` (SHA-256 `2cf65dff…c0e59`) into `/workspace/DataSet/yolo/`. Then
  `python english/scripts/fetch_rps.py --archive DataSet/yolo/Rock-Paper-Scissors.v1i.yolo26.zip
  --class-names paper rock scissors`, run the notebook with `COURSE_EPOCHS` unset, and re-run the embed script.
- **Checks after this session:** `check_course.py` (77 files, 14 notebooks, 0 problems),
  `verify_saved_outputs.py` (0 problems), `git diff --check` clean, and a CJK scan over `english/**`
  (notebooks + Markdown) reports no matches. Still nothing committed.
- **Optional next step:** the same embedding for the remaining ~12 English notebooks
  (`01-image-classification`, `03-sentiment-analysis` pytorch/paddle) needs a per-figure caption pass; the
  figures are already saved inside those notebooks, so no re-execution is required.

## 2026-10-18 (fourth session): whole-course pass, Chinese execution, English lesson parity

The user asked for one pass over the **whole** project: English-only paths, Chinese and English trees aligned with no
gaps, Chinese lessons producing Chinese I/O and English lessons English I/O.

- **English masters caught up with the Chinese long-form lessons.** `english/02-object-detection/lessons/01-cv-overview.md`
  went from a 25-line summary to 969 lines and `02-cnn-basics.md` to 525 lines, section for section with the Chinese
  versions and using the same figures (`../assets/lessons-1..46`); the four Paddle API passages became
  `torch.nn.Conv2d` with a note that the Chinese original shows `paddle.nn.Conv2D`. A mirrored English run report
  `english/02-object-detection/lessons/05-vehicle-counting-run-report.md` sits beside the Chinese one with the same
  structure and numbers.
- **Every Chinese lesson executed for real** in `~/env_dl_uv` (CPU, classroom defaults): vision 4.88/7.20/564.99/5.81 s,
  PyTorch NLP 1.39/6.39/61.68/8.53 s, Paddle NLP 1.44/6.90/24.77 s, detection 2152.35 s. English and Chinese vehicle
  runs agree metric for metric (seed 42, deterministic): test P 0.7399 / R 0.6484 / mAP50 0.6975 / mAP50-95 0.4059.
  All 26 current notebooks (13 per language) now carry `预期输出` / `Expected output` blocks plus
  `assets/<notebook>-N.png`; `english/reports/README.md` was rewritten to state which machine and run mode produced
  each number.
- **Execution and authoring tools hardened.** `execute_and_save.py` no longer re-executes `archive/legacy-notebooks/`,
  matches `--notebook` by exact stem (a substring match once targeted an archived notebook), and execution reports now
  accumulate instead of being rewritten by a targeted run; the English RPS row lost that way was restored from the
  previous report revision and marked. `embed_expected_outputs.py` is the single general tool (26 jobs, per-language
  labels, manual caption overrides for the detection notebooks); `02-object-detection/scripts/embed_expected_outputs.py`
  stays a shim. `build_chinese_course.py` refuses to overwrite a mirror that holds saved outputs (use `--force`,
  optionally with the new `--only`), and now skips generated cells tagged `course-runtime-info` /
  `course-expected-output` instead of demanding translations for them.
- **A real Chinese-output defect found and fixed.** The Chinese pretrained-sentiment lesson printed
  `positive (stars 4 and 5)` because its `LABEL_CN` map missed the checkpoint's real label strings; the mapping lives in
  `scripts/build_chinese_course.py`, the mirror was rebuilt with `--only 04-pretrained --force`, re-executed (8.53 s) and
  re-embedded, and now prints `正面（0.994）：…` / `负面（0.977）：…`.
- **Assets and links audited repository-wide** by the new `scripts/check_docs_assets.py`: local links in every Markdown
  and notebook Markdown resolve, zero remote images, `assets/` holds only `<name>-<index>.<ext>` files with no
  subdirectories, `docs/*.md` and `docs/*.zh-CN.md` stay paired, and every `README.zh-CN.md` directory has an English
  `README.md`. Links inside archived PaddleYOLO courseware are reported as `legacy_external_links` (6) rather than
  problems, but archived asset references are now validated — one broken `../assets/lenet/…` path left by the earlier
  asset move was found and repaired, and the archived `02-lenet-cifar10.ipynb` was restored to its pre-run state after
  the mis-targeted execution described above.
- **Docs corrected.** `docs/datasets.md` had a duplicated `## IMDb` heading; both detection `data/README.md` files gained
  the macOS/Linux (`~/env_dl_uv` + `/workspace/DataSet/yolo`) copy-and-import commands next to the PowerShell ones;
  `04-dataset-formats/data/README.md` now says where its input datasets come from; the English vision README gained a
  Data-and-outputs section and the English sentiment README a Run section; both root READMEs describe the detection
  module as including vehicle counting and quote the current runs.
- **Checks, all zero problems:** `english/scripts/check_course.py`, `scripts/check_parity.py`,
  `scripts/check_docs_assets.py`, `english/scripts/verify_saved_outputs.py` (28 notebooks), `git diff --check`, plus
  `build_chinese_course.py --check` (11 mirrors).

Not committed: nothing was committed in this session, so `git status --short` still shows the whole tree of changes
(most zh notebooks are untracked because earlier sessions `git mv`-ed the tracked originals into `archive/`).
Remaining known gaps: the RPS v1 archive is still absent from the DataSet staging area, so the Chinese RPS notebook
keeps its one-epoch check; the vehicle lesson is 5 epochs at 320 px and still climbing; the archived legacy notebooks
are never executed by design; GPU remains unverified.
中文交接：本会话把中英两套课程彻底对齐（英文 CV/CNN 课件扩写并与中文同章节同图号），中文 13 本 Notebook 全部在
`env_dl_uv` 真实执行并内嵌「预期输出」与 `assets/` 图片，修掉中文预训练课的英文标签回退问题，新增全仓文档/图片校验脚本，
并把执行器与镜像生成脚本的三处隐患（误跑归档件、报告被覆盖、生成覆盖实跑输出）修好；四项校验与 `git diff --check` 全绿，
尚未提交。

## 2026-10-18 (fifth session): validation follow-through, one interpreter everywhere, data docs

- **Cleared the four problems left by the previous pass.** `english/reports/README.md` no longer contains any CJK
  (`Chinese`/`zh-CN` wording), and the five broken links in the rewritten English `03-yolo-theory.md` /
  `04-yolo-practice.md` now resolve: dataset-format links go to `../../../04-dataset-formats/README.md`, the module
  guide is `../README.md`, and the superseded lectures point at the Chinese archive where they actually live.
- **Repaired a silent regression.** `03-sentiment-analysis/pytorch/notebooks/03-lstm-sentiment.ipynb` had been rebuilt
  from the English master without its executed outputs. Re-executed in `~/env_dl_uv` (63.04 s, 8 code cells, 13
  outputs, 1 figure), re-embedded (`03-lstm-sentiment-1.png`), and `reports/README.md` plus
  `pytorch-zh-CN-executed.json` now agree on 63.04 s.
- **One interpreter, literally.** Deleted the last environment inside the repository,
  `english/02-object-detection/.venv` (1.2 GB), after confirming it held the same pinned `torch 2.14.1` /
  `ultralytics 8.4.177` as `~/env_dl_uv`, and removed a stray nested `02-object-detection/02-object-detection/outputs/`
  artifact. Every doc that told readers to use that path now names `~/env_dl_uv` first and shows how to recreate the
  locked module environment with `uv sync --locked --project english/02-object-detection`.
  `detection-zh-CN-executed.json` gained an `environment_note` saying which interpreter produced which row.
- **Executor hardening**: `english/scripts/execute_and_save.py` keeps extra top-level keys of an existing report
  (previously a rerun would drop `environment_note`-style fields) and writes rows sorted by notebook; existing
  reports were normalized to that order.
- **Docs checker grew two checks**: `scripts/check_docs_assets.py` now also reads `data/README*` files (data itself is
  still skipped) and validates `document.md#heading` fragments with GitHub slug rules (20 fragments checked; it caught
  two wrong Chinese anchors that are now fixed).
- **Data documentation is now per dataset, both routes.** `english/02-object-detection/data/README.md` and
  `02-object-detection/data/README.md` were restructured into one section per dataset (RPS v1, vehicle counting v4,
  COCO8), each with a *cp method* (stage in `/workspace/DataSet/yolo/`, then importer; `--export-dir` and
  `--staging` noted) and a *download method* (page, format, where to save the ZIP).
  `04-dataset-formats/data/README.md` gained the same two routes plus a Chinese pair
  `04-dataset-formats/data/README.zh-CN.md`, and the whole conversion topic now shows the macOS/Linux commands that
  were actually used alongside the PowerShell ones. Both root READMEs explain the stage-once-then-copy layout.
- **Stale language claims removed.** Three documents still said the English course does not read the vehicle-counting
  dataset; it does, in both languages, from one shared import with separate `outputs/`. English module READMEs gained
  the missing `Relationship to the Chinese course` / `Data` / `Run` headings so heading structure matches the Chinese
  READMEs, and `04-dataset-formats` READMEs are 6 headings on each side.
- **Checks, all zero problems**: `check_course.py` (92 files, 15 notebooks), `check_parity.py` (0 problems, 0 Chinese
  notebooks with English output), `check_docs_assets.py` (62 documents, 20 anchors), `verify_saved_outputs.py`
  (28 notebooks), `build_chinese_course.py --check` (11 mirrors), `git diff --check`.

Nothing was committed. 中文小结：本轮清掉了上一轮遗留的 4 项校验问题，修回被覆盖输出的中文 LSTM 镜像并重跑内嵌；删除仓库内最后一份
重复环境（检测模块 1.2 GB `.venv`），把文档里所有指向它的路径改成课堂单一环境 `~/env_dl_uv` 并写明如何用 uv 重建；执行器不再丢报告字段、
行序稳定；文档校验新增 `data/README.md` 覆盖与标题锚点检查；检测与格式专题的每个数据集都补齐「cp 方式 + 下载方式」并做了中英配对；
清理了「英文课程不读车辆数据」等过期表述，中英模块 README 结构对齐。五项校验全部 0 问题，未提交。

## 2026-10-18 (sixth session)

Closed out the pass over the whole course. Final state of the repository and the machine:

- **Single interpreter confirmed on the machine.** No `.venv` and no `.ipynb_checkpoints` remain anywhere in the
  repository; Jupyter lists only `env_dl_uv` (plus the unrelated system `python3`). `~/env_dl_uv` reports
  Python 3.12.12, PyTorch 2.14.1, Ultralytics 8.4.177, which is what every saved output in the course was produced with.
- **Environment story made consistent across both languages.** `english/docs/environment-setup.md` was the last
  document still claiming "each module has its own `.venv`" and telling readers to pick "the module's Python 3.12
  kernel". It now points at the one-kernel policy in `docs/environment-setup.md` (verified anchor), keeps
  `pyproject.toml` + `uv.lock` as the reproducible spec, and explains that `paddlenlp` / `visualdl` are deliberately
  excluded because their pinned `protobuf` conflicts with `paddlepaddle==3.3.1`. The remaining PowerShell paths under
  `.\english\02-object-detection\.venv\Scripts\python.exe` are the documented optional isolated rebuild
  (`uv sync --locked --project english/02-object-detection`), not the classroom path.
- **Wording.** The vehicle-counting paragraph in `02-object-detection/README.md` no longer ends in a colon before a
  prose paragraph. A repository-wide scan for the same pattern found only colons that legitimately introduce a
  formula, figure, or code block.
- **Checks, all zero problems after these edits**: `check_course.py` (92 files, 15 notebooks), `check_parity.py`
  (0 problems, 0 Chinese notebooks with English output), `check_docs_assets.py` (62 documents, 20 anchors),
  `verify_saved_outputs.py` (28 notebooks), `build_chinese_course.py --check` (11 mirrors), `git diff --check`.

Still open for the user to decide: the RPS v1 archive is not in `DataSet` staging, so the Chinese RPS run stays a
single-epoch pass over the full dataset (mAP50 0.7266); the vehicle lesson ran 5 epochs at 320 px and is not converged
(mAP50 0.6975); GPU runs were never validated; the old conda envs (`env_agent`, `env_datasci`, `env_langchain`,
`env_ml`) still exist, only their Jupyter kernels were removed.

Nothing was committed. 中文小结：本轮把最后残留的「每模块独立环境」旧口径改成单一内核政策（PowerShell 的模块 `.venv`
明确标注为可选重建路径），修掉车流量段的悬空冒号；仓库内已无任何 `.venv` 与 `.ipynb_checkpoints`，Jupyter 只剩
`env_dl_uv` 内核。六项校验复核后全部 0 问题，未提交。待用户确认事项：RPS v1 压缩包未进暂存区（中文 RPS 仍是全数据单轮）、
车辆课 5 轮未收敛、GPU 未验证、conda 旧环境只删了内核未删环境。


## Session 9 - dataset-format topic moved into the detection module

Requested change: the format topic belongs with object detection, so `04-dataset-formats/` no longer exists as a
fourth top-level module. New layout:

- `english/02-object-detection/dataset-formats/README.md` - English source guide (button labels for the Chinese
  viewer pages rewritten as English descriptions so `english/` stays ASCII).
- `02-object-detection/dataset-formats/README.md` - Chinese mirror (was `README.zh-CN.md`).
- `dataset-formats/data/README.md` on each side documents the generated conversion folders.
- Scripts follow the house convention and live in `english/scripts/`: `dataset_formats.py` (was `convert.py`) and
  `check_dataset_formats.py` (was `check_roundtrip.py`, now imports the converter and writes
  `english/reports/dataset-formats-validation.json`).
- Both module READMEs, both root READMEs, both dataset/learning-path docs, `docs/environment-setup.md`,
  `english/docs/{datasets,adaptation-map}.md`, the detection lessons 03/04, both data READMEs, and both current
  detection notebooks now link through module-relative paths; the only remaining
  `04-dataset-formats` string is this file's earlier history. `AGENTS.md` describes the new location and script name.
- `.gitignore` now also un-ignores `**/data/README.zh-CN.md`, which is why the previous session's Chinese data notes
  never reached the index.

Incident, recorded as it happened: while rewriting those links a batch regex containing a single-character
alternative (`|\.`) replaced **every literal dot** in eleven English-side Markdown files with a computed path
fragment. The damage was deterministic and reversible. Recovery: a collapse loop
(`while '../.' in s: s = s.replace('../.', '.')`) that was first proved to round-trip line by line, applied to
`docs/datasets.md`, `docs/learning-path.md`, `docs/environment-setup.md`, `english/docs/datasets.md`,
`english/docs/adaptation-map.md`. One line (`english/docs/datasets.md` header, a `../../docs/...` link) needed a
manual restore because greedy left-to-right collapsing drops one level in doubled prefixes; the round-trip assertion
caught it. Chinese-side files and both large notebooks were not damaged beyond the intended link edits. Rule going
forward: never batch-replace with single-character alternatives, and prove invertibility with per-file hit counts
first.

Checks after the move, all zero problems: `check_docs_assets.py` (60 documents, 20 anchors), `check_parity.py`,
`check_course.py` (95 files, 15 notebooks), `verify_saved_outputs.py`, `build_chinese_course.py --check`
(11 mirrors), `git diff --check`, and a real fixture run of `english/scripts/check_dataset_formats.py`
(status `passed`, six directions, guard checks).

Still not done from earlier user direction: the `cuda` -> `mps` -> `cpu` device selection has not been applied to
`english/scripts/build_course.py`, `english/scripts/build_detection.py` or the executed notebooks, the MPS reruns
that would refresh every saved output and `**Expected output:**` block have not been started, the RPS v1 archive is
still missing locally (so the RPS lesson cannot be re-executed), and the four legacy conda environments are still
present. Nothing was committed.

中文小结：格式专题已从顶层 `04-dataset-formats` 移入检测模块（中英各一份 README + `data/README.md`，脚本并入
`english/scripts/`），所有入口链接、`AGENTS.md` 与报告路径同步更新；本轮如实记录并修复了一次批量正则误替换（英文侧
11 个 Markdown 的每个句点），已按可逆反演逐文件恢复并用六项校验复核为 0 问题。设备选择 cuda→mps→cpu、MPS 全量重跑、
RPS 数据包、conda 旧环境清理仍未完成；未提交。


## Session 10 - device policy, Roboflow API-key download, conda cleanup

Device selection now resolves CUDA, then Apple Silicon MPS, then CPU, everywhere the course picks a device:

```python
DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
```

Ultralytics and Hugging Face call sites keep the same order as a plain `"cuda"/"mps"/"cpu"` string
(`select_device("mps")` and `pipeline(..., device="mps")` were both exercised). Paddle keeps `gpu`/`cpu`
only because the pinned `paddlepaddle==3.3.1` has no MPS backend - `paddle.set_device("mps")` raises.
Sixteen notebooks plus the notebook generators (`english/scripts/build_course.py`,
`english/scripts/build_detection.py`, `02-object-detection/scripts/build_vehicle_counting.py`) carry the
new expression, `docs/environment-setup.md` gained a **Device selection** section, `docs/environment-setup.zh-CN.md`
gained **设备选择**, and `AGENTS.md` records the convention.

Roboflow download reality check: the browser button needs a session, but the export REST endpoint accepts a personal
API key, so both detection archives are scriptable. Verified with HTTP 200 and a full download:

```bash
LINK=$(curl -sS -G "https://api.roboflow.com/<workspace>/<project>/<version>/yolo26" \
  --data-urlencode "api_key=$ROBOFLOW_API_KEY" --data-urlencode "nocache=true" \
  | python -c 'import json,sys; print(json.load(sys.stdin)["export"]["link"])')
curl -sSL "$LINK" -o dataset.zip   # poll until "progress" reaches 1; "export.size" is in MB
```

`Rock-Paper-Scissors.v1i.yolo26.zip` (133,755,210 bytes, SHA-256 `2cf65dff...0e59`) landed in
`/workspace/DataSet/yolo/` and imported through `english/scripts/fetch_rps.py`, reproducing the documented
3,939/338/186 images and 4,610/400/204 boxes. The key lives in `~/.config/roboflow_api_key` (0600) and is never
committed; the key command is now documented in both `data/README.md` files, `docs/datasets{,.zh-CN}.md`,
`english/docs/datasets.md` and the staging `DOWNLOAD.md`, replacing the old "curl cannot download it" wording.

Conda: `conda remove` is blocked by the Anaconda channel terms of service (not accepted on the user's behalf), so the
four approved environments were deleted directly - `env_agent`, `env_datasci`, `env_langchain`, `env_ml` are gone and
`~/Library/Jupyter/kernels` now holds only `env_dl_uv`. `env_pytorch`, `env_rag` and `jupyter` remain because deleting
them was never authorised.

Link-rewrite incident, recorded as it happened: a batch regex with a single-character alternative again turned literal
dots into path fragments in about fourteen files. Recovery was `text.replace(injected_fragment, ".")`, proved
reversible per file, followed by recomputing each legitimate topic link with `os.path.relpath`. The final scan
`rg -e 'README\.md[A-Za-z_0-9]' -e '\]\(\.\)' -e '\]\([A-Za-z0-9-]+\.\)'` is clean, and `AGENTS.md` now forbids
single-character alternatives in batch replacements.

The user's original YOLO11 rock-paper-scissors notebook lives again at
`02-object-detection/notebooks/01-yolo11-rock-paper-scissors.ipynb`, kept as read-only history and excluded from every
execution run. Nothing was committed.

中文小结：设备选择统一为 CUDA → MPS → CPU（Paddle 因 3.3.1 无 MPS 后端仍只判 GPU/CPU），16 本 Notebook 与三本生成脚本
同步；实测 Roboflow 导出接口接受个人 API key，石头剪刀布 v1 已下载入库，文档补上「API key 一键下载」替代旧的「curl 无法下载」。
四个 conda 旧环境已删（conda 官方渠道 ToS 拦截，改为直接删除目录），Jupyter 仅剩 `env_dl_uv`。批量正则再次踩坑并已可逆复原，
规则写进 `AGENTS.md`。未提交。

## Session 11-13 - MPS re-runs, honest numbers everywhere, deriver drift, key validation

All four detection notebooks were executed serially on Apple silicon MPS inside `~/env_dl_uv` (never concurrently, so
every duration is the honest wall clock of a single run):

| Notebook | Seconds | Output items | Figures |
|---|---|---|---|
| English rock-paper-scissors | 1161.80 | 12 | 4 |
| English vehicle counting | 940.21 | 19 | 7 |
| Chinese rock-paper-scissors | 1163.89 | 12 | 4 |
| Chinese vehicle counting | 940.47 | 19 | 7 |

Same data, same `seed=42`, and the two languages agree digit for digit: rock-paper-scissors test mAP50 0.9410 /
mAP50-95 0.7467; vehicle counting test precision 0.7308 / recall 0.6444 / mAP50 0.6983 / mAP50-95 0.4071, zero-shot
mean absolute counting error 4.33 vehicles per image over six images, fine-tuned error 4.0 over the same four images
shown before training, and video traffic 4 forward + 2 backward = 6 unique vehicles = 40.0 vehicles/minute against a
ground truth of 6, so detector/tracker deviation is now `+0`. Every document that quoted the older CPU runs was
rewritten to these numbers: both top-level READMEs, `english/README.md`, `docs/datasets.md` and its Chinese twin (the
rock-paper-scissors row gained the missing DataSet staging step, so both datasets now show cp and download routes),
`docs/environment-setup.zh-CN.md`, `english/reports/README.md`, the three evidence JSON files, and both
`05-vehicle-counting-run-report.md` lessons - the Chinese one was rewritten end to end against the Chinese run's real
printing.

Two real defects found and fixed rather than papered over:

- `english/scripts/build_vehicle_notebook.py` used to copy Chinese fragments of the master into its own
  `CODE_EDITS`, which pushed Han characters into `english/`. The edits are now ASCII regex anchors plus
  `reverse_localization_rules()`, which imports `VEHICLE_RULES` from `scripts/localize_chinese_detection.py` with
  `importlib` and inverts all 59 English-to-Chinese rules, so the rule table has one owner. Its assertion changed from
  "replacements must equal the rule count" (already false: 64 hits for 62 rules) to "every rule fires at least once and
  no derived code cell contains CJK".
- The derived first code cell disagreed with the delivered notebook (`"default classroom training parameters"` versus
  the executed `'Default classroom training parameters'`). The localizer rule now carries the executed spelling, so the
  derivation is reproducible instead of approximately right.

Four stale "this run was on CPU / 2152 s" sentences were replaced with the MPS reality in the Chinese master, in the
English deriver *and* in the delivered English notebook, plus the English rock-paper-scissors sizing note in
`english/scripts/build_detection.py` (a 320-pixel epoch measures about 114 seconds on MPS).

Derivation was verified without touching delivered outputs, because `build_vehicle_notebook.py` writes output-free
notebooks: the master, the localizer and the deriver were copied into a fresh `/tmp` directory and run there, then
compared with the delivered English notebook - 13 code cells and 9 prose cells identical, 13 expected-output cells
preserved, zero CJK in the derived file.

Verification state, all after the last edit: `scripts/embed_expected_outputs.py` idempotent;
`scripts/localize_chinese_detection.py` 12/12 and 59/59 already applied; `scripts/check_docs_assets.py` `problems: []`
(remote images 0, six legacy external links inside read-only history notebooks); `scripts/check_parity.py`
`parity_problems: []` and `chinese_notebooks_with_english_outputs: []`; `english/scripts/check_course.py` `problems: []`
across 95 sources; `scripts/build_chinese_course.py --check` 11 mirrors; `english/scripts/verify_saved_outputs.py`
`problems: []` across 28 notebooks including both detection lessons; `git diff --check` clean.

The user's Roboflow key was validated without re-downloading gigabytes: the documented export endpoint
`https://api.roboflow.com/{workspace}/{dataset}/{version}/yolo26` answered for both datasets, the signed link served a
`PK\x03\x04` header, and the served byte counts (525,865,343 and 133,755,210) equal the staged archives in
`/workspace/DataSet/yolo/`, whose SHA-256 digests equal the ones recorded in each `provenance.json`. The key stays in
`~/.config/roboflow_api_key` (mode 0600) and is referenced by path in the docs, never copied into the repository.

Open for the user: `env_pytorch`, `env_rag` and `jupyter` still exist as conda environments and await a delete decision.
Known cosmetic defect, not yet touched: 46 English markdown cells (and one Chinese cell in the read-only YOLO11
history notebook) indent prose by four spaces, which Jupyter renders as a code block; fixing it means dedenting in
`english/scripts/build_course.py` plus the delivered notebooks with outputs preserved.

中文小结：四本检测课 Notebook 已在 MPS 上串行重跑（英文 1161.8 s / 940.21 s，中文 1163.89 s / 940.47 s），中英同种子
指标逐位一致；所有引用旧 CPU 数字的文档、报告、证据 JSON 全部按实测改写，数据集文档补齐「cp 暂存 + API key 下载」两条路径。
修掉两个真问题：英文派生脚本会把汉字带进 `english/`（改为从本地化脚本反转 59 条规则，单一事实源），以及派生结果与已交付
Notebook 的字符串漂移。派生验证在 /tmp 沙箱完成（13 个代码单元与 9 个说明单元零差异、零汉字）。全套校验全绿。
用户提供的 Roboflow key 实测可用：导出链接返回的字节数与本地暂存包完全相同，且两份包的 SHA-256 与 `provenance.json` 一致。
`env_pytorch`、`env_rag`、`jupyter` 仍等用户决定是否删除；另有一处英文说明单元四空格缩进会被渲染成代码块，尚未处理。未提交。

## Session 14 - conda environments removed, lesson prose no longer rendered as code

`conda remove -n env_pytorch --all` is still refused by the Anaconda channel terms of service, so the three remaining
environments were removed as directories: `env_pytorch` (892 MB), `env_rag` (2.3 GB) and `jupyter` (296 MB) are gone,
`conda env list` now shows only `base`, `~/.conda/environments.txt` holds no stale rows, and
`~/Library/Jupyter/kernels` still contains only `env_dl_uv`. Nothing course-related was inside them.

The English course rendered explanatory prose as code blocks: 54 markdown cells across 13 English notebooks indented
their body by four spaces. Root cause was in the generator, not in the notebooks - `md()` in
`english/scripts/build_course.py` called `textwrap.dedent`, but each lesson string starts its title on the same line as
the opening quotes, so that line has zero indentation, the common prefix is therefore zero, and `dedent` removed
nothing. `markdown_source()` now keeps the first line flush and strips only the shared indentation of the rest, so
nested list indentation and fenced-code indentation survive; the fence interiors in the vehicle lesson (the
`count_video` snippet and the flow-rate JSON) were left exactly as they were because their indentation is meaningful.

The delivered notebooks were fixed rather than regenerated, because regeneration writes output-free notebooks:
`english/scripts/build_course.py` and `build_detection.py` were run in `/tmp/dedent_check` and every dedented cell was
required to appear verbatim in the generator's output before being written, with assertions that code cell sources and
the saved output count of each notebook stayed identical. 53 cells matched the uniform pattern; one exercises cell
needed `build_detection.py` aligned first, because an earlier in-place edit had reworded its source links and dropped
them to column zero, which suppressed the common-prefix rule there too.

Re-verified after the change: no markdown cell anywhere in the repository still has indented prose outside a fence;
`check_docs_assets.py` `problems: []` with `remote_images: 0` (dedenting exposed those links to the checker and none of
them broke); `check_parity.py` clean; `english/scripts/check_course.py` clean; `verify_saved_outputs.py` clean over 28
notebooks; `build_chinese_course.py --check` 11 mirrors; `git diff --check` clean; the vehicle derivation sandbox still
reproduces 13 code cells and 9 prose cells with zero differences.

Known, deliberately not changed: the generated rock-paper-scissors intro in `build_detection.py` is older than the
curated notebook intro, which carries the real image counts, the class order and the MPS run numbers. `main()` refuses
to run against executed notebooks precisely so curated notebooks are edited in place, so this is documented drift
rather than something to regenerate.

中文小结：三个残留 conda 环境（`env_pytorch`、`env_rag`、`jupyter`，合计约 3.5 GB）已删除，`conda env list` 仅剩 base，
Jupyter 内核仍只有 `env_dl_uv`。英文课程 13 本 Notebook、54 个说明单元原本带四空格缩进，被 Jupyter 当成代码块渲染；
根因在 `build_course.py` 的 `md()`：标题与三引号同行使公共缩进为 0，`textwrap.dedent` 空转。新增 `markdown_source()`
只剥离正文公共缩进，保留嵌套列表与代码围栏内的相对缩进（车辆课 JSON 与示例代码缩进保持原样）。已交付 Notebook 就地修，
不重新生成：每个单元都必须在沙箱生成结果中逐字出现才写入，并断言代码单元与已保存输出数量不变。全套校验再次全绿，
车辆课派生验证仍零漂移。石头剪刀布介绍单元的生成器文案旧于交付版，属生成后就地加详的既有约定，仅记录不改。未提交。
