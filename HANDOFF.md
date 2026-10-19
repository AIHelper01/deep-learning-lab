# Project handoff

Updated: 2026-10-19 (Asia/Shanghai). Session 21 is committed on `main` together with its entry and has not been pushed; Sessions 18, 19 and 20 are committed together as `750f381` on main and have not been pushed; Session 15 is committed on main together with its entry and has not been pushed.
Each earlier session states its own commit state in its closing line.

## Session 21 - one uv project at the repository root replaces the per-module environments

The course is launched with uv, but the repository root had no `pyproject.toml`, no `uv.lock` and no
`.python-version`: a fresh clone could not `uv sync` anything. Dependency declarations lived in 7
module `pyproject.toml`, 4 English `uv.lock`, 8 module `.python-version` and 9 module
`requirements.txt`, and the two newest of those lock sets disagreed with the interpreter that
actually produced every saved output (torch 2.8.0 / paddlepaddle 2.6.2 on the Chinese side,
torch 2.14.1 / paddlepaddle 3.3.1 on the English side). The user asked for the repository to be
out-of-the-box runnable with the uv files at the root, and for the subdirectories to stop carrying them.

Added at the root, as a virtual project (`[tool.uv] package = false`, `requires-python = ">=3.12,<3.13"`):

- `pyproject.toml` - 27 declared dependencies, derived two ways and cross-checked: the versions actually
  installed in the validated `~/env_dl_uv`, and an import scan of every committed notebook plus
  `common/`, `english/common/`, `scripts/` and `english/scripts/` (IPython, PIL, cv2, gensim, jieba,
  joblib, lightgbm, matplotlib, nbclient, nbformat, numpy, onnxruntime, paddle, pandas, pyarrow,
  requests, seaborn, skl2onnx, sklearn, torch, torchvision, transformers, ultralytics, xgboost, yaml).
  `lapx` is declared because Ultralytics' ByteTrack path imports it without depending on it;
  `setuptools` because Paddle imports it; `pyarrow` because `english/common/vision_data.py` imports it
  lazily for the CIFAR Parquet fallback. `tensorboard` is not declared: nothing imports it and it was
  not installed in the validated environment either.
- `.python-version` (`3.12`) and `uv.lock` - 168 packages, and the lock keeps `macosx_11_0_arm64`,
  `manylinux1_x86_64` and `win_amd64` wheels for `paddlepaddle==3.3.1`, so one lock covers the
  macOS classroom machine and the Windows launcher target.
- 26 module-level env files removed (7 `pyproject.toml`, 4 `uv.lock`, 8 `.python-version`,
  7 `requirements.txt`); `archive/environment/` keeps its 3 historical sets untouched as history, which
  is why `archive/environment/README.md` still points at them.

Launchers and guard:

- `start-notebooks.ps1` now routes both languages itself (English under `english/`, Chinese at the
  root), runs `uv sync --locked` once at the repository root, then
  `uv run jupyter lab --notebook-dir <module>/notebooks`; the old per-module
  `.venv/Scripts/python.exe` requirement is gone.
- `english/start-notebooks.ps1` is now a shim that forwards `-Language`, `-Module` and `-DryRun` to the
  root launcher, keeping its `vision` default because it is documented and tested.
- `tests/check-launcher.ps1` was rewritten for the new contract: root `pyproject.toml`/`uv.lock`/
  `.python-version` must exist, every route's `ProjectRoot` must be the repository root, Chinese routes
  must stay out of `english/`, the shim must keep its default and forward `zh-CN`, and none of the 7
  module directories may keep a `pyproject.toml`, `uv.lock`, `.python-version` or `requirements.txt`.

Documentation, 29 Markdown files: about 90 `~/env_dl_uv/.venv/bin/python ...` and
`.\english\02-object-detection\.venv\Scripts\python.exe ...` command prefixes became
`uv run python ...` (uv walks up to the root manifest, so `uv run` works from any subdirectory and no
command needs `--project`); the `py=` / `$py =` helpers in the dataset-format topic now point at the
root `.venv`; both environment guides were rewritten around the root project, keeping the
`#one-kernel-for-the-whole-course-macoslinux` and `#device-selection` anchors that other pages link to;
`english/docs/environment-setup.md` replaced the deleted per-module `requirements.txt` pip path with a
`uv export --locked --no-hashes --no-emit-project` fallback that still builds one environment; and
`~/env_dl_uv` is now documented as what produced the committed evidence, not as the setup path.

Verified: `uv lock` resolves 168 packages; `uv sync --locked` builds the root `.venv` on Python 3.12.12;
`uv sync --locked --check` reports "Would make no changes"; an import smoke test of all 25 course
third-party modules plus `lap` and `ultralytics.nn.tasks` passes (torch 2.14.1, MPS available,
numpy 1.26.4 - the same versions as the validated interpreter); `uv run python` from
`02-object-detection/` resolves the root project without `--project`; `uv run jupyter --version` and
`execute_and_save.py --help` work. All seven checks are green: `verify_saved_outputs.py`
(30 notebooks, 0 problems), `check_parity.py` (42 notebooks, 0 problems, the known 81 English-figure
prose items in Chinese masters unchanged), `check_docs_assets.py` (0 problems),
`english/scripts/check_course.py` (92 sources, 16 notebooks, 0 problems),
`build_english_course.py --check` (1 mirror), `build_chinese_course.py --check` (11 mirrors),
`git diff --check` clean.

Not verified: `pwsh` is not installed on this machine, so `tests/check-launcher.ps1` was never executed -
its route assertions were reproduced in Python against the real filesystem (every route's module and
notebook directory exists, no module-level env file survived) and the two scripts reuse constructs the
previous versions already used. No notebook was re-executed: the saved outputs are the committed
evidence produced in `~/env_dl_uv` on these same locked versions, and re-running would rewrite them.

Commit state: this session's 60 files and this entry go into one commit on `main`; nothing is pushed.

中文小结：课程是 uv 启动的，但仓库根没有 `pyproject.toml`/`uv.lock`/`.python-version`，克隆下来 `uv sync` 无从下手；依赖散在
7 份模块 pyproject、4 份英文 uv.lock、8 份 `.python-version`、9 份 requirements.txt 里，而且最新的两套锁定与真正跑出全部「预期输出」的解释器并不一致（中文侧 torch 2.8.0 / paddle 2.6.2，英文侧 torch 2.14.1 / paddle 3.3.1）。按要求把 uv 工程收编到仓库根：新增根 `pyproject.toml`（27 项依赖，按已验证 `~/env_dl_uv` 的实际版本 + 全仓 notebook 与脚本 import 扫描双向对齐；`lapx`/`setuptools`/`pyarrow` 这类运行期才 import 的补齐；`tensorboard` 没人用也不装）、根 `.python-version`（3.12）与 `uv.lock`（168 个包，paddle 同时含 macOS arm64 / manylinux x86_64 / win_amd64 wheel，一份锁覆盖课堂 Mac 与 Windows 启动器），删掉 26 份模块级环境文件，`archive/environment/` 的 3 份历史记录原样留着。启动器改为两侧共用根工程（`uv sync --locked` + `uv run jupyter lab --notebook-dir <模块>/notebooks`），`english/start-notebooks.ps1` 退化成转发的薄壳，`tests/check-launcher.ps1` 重写为校验根三件套、各路由 `ProjectRoot` 都是仓库根、中文路由不落进 `english/`，并反向钉住 7 个模块目录不得再留任何环境文件。29 份文档同步：约 90 处 `~/env_dl_uv/.venv/bin/python`/模块 `.venv\Scripts\python.exe` 命令统一成 `uv run python`（uv 会向上找到根 pyproject，任何子目录都不用 `--project`），两篇环境指南按根工程重写并保留被引用的 `#one-kernel-...`、`#device-selection` 锚点，英文篇用 `uv export` 方案替换被删的模块 requirements 路径，`~/env_dl_uv` 改为「产出既有证据的解释器」而不再是安装路径。验证：`uv lock` 168 包、`uv sync --locked` 建出 Python 3.12.12 的 `.venv`、`--check` 报 Would make no changes、25 个课程第三方模块 + `lap` + `ultralytics.nn.tasks` 全部导入通过（torch 2.14.1、MPS 可用、numpy 1.26.4），在 `02-object-detection/` 里 `uv run` 免 `--project` 可用；七项校验全绿（30 本输出一致性、42 本对齐、文档链接、92 源/16 notebook 英文检查、1 + 11 份镜像、`git diff --check`）。本机没有 `pwsh`，启动器测试脚本没能真跑，只按同样断言在 Python 里逐条核对了路由与文件；本轮没有重跑任何 notebook，已保存输出就是既有证据，重跑会改写它们。60 个文件与本篇进同一个 `main` 提交，未推送。


## Session 20 - the English side of modules 01-03 is audited against the Chinese masters

The user asked whether `english/01-image-classification`, `english/02-object-detection` and
`english/03-sentiment-analysis` are missing anything, now that the Chinese tree is the master.
`check_parity.py` was green the whole time, which is exactly the problem: it never looked at committed
documents inside `data/` and `outputs/`, and nobody had re-read the archive and route READMEs after the
direction flip.

Fixed:

- Two committed documents existed only on the Chinese side
  (`03-sentiment-analysis/outputs/paddle/README.md`, `.../outputs/pytorch/README.md`); the English twins
  are now written. They could never have been committed before: `english/.gitignore` had
  `**/outputs/**` with a top-level `!**/outputs/README.md` only, while the root file also re-includes
  `!**/outputs/**/` and `!**/outputs/**/README.md`. The nested negations are now in both files.
- `scripts/check_parity.py` now treats a `README.md` under `data/` or `outputs/` as a course document
  when it belongs to the repository (`git ls-files --cached --others --exclude-standard`), so local
  download notes and caches stay out of pairing while authored guides cannot be one-sided again.
  Verified with a probe file: the check reports the missing English twin and goes quiet once removed.
- 16 statements in 12 files still said English was the master - module READMEs for 01 and 03 on both
  sides, plus all six `archive/legacy-notebooks/README.md`. Each now states the repository rule
  (Chinese master) together with the Migration status (these two modules' generator still keys on
  English text, so do not regenerate either side from the wrong direction), which is what the
  `AGENTS.md` rule already said.
- `english/01-image-classification/archive/legacy-notebooks/README.md` was the generic NLP template and
  contradicted its Chinese master. It now mirrors that master: the vision-specific archiving reasons
  (including the notebook-directory working convention), the `--include-legacy --cwd notebook` rerun
  commands, the per-notebook status table with the recorded numbers, and the two genuine skips
  (old-server ResNet checkpoint, missing LEDNUM images).
- `english/03-sentiment-analysis/pytorch/README.md` and `.../paddle/README.md` both shipped a leaked
  template placeholder, `03-sentiment-analysis/$d/`; each now names its own route.
- `english/01-image-classification/README.md` and `english/03-sentiment-analysis/README.md` lacked the
  "Chinese course / Project" header line that the detection module already had, and the English
  detection lesson list stopped at 7 while the Chinese master lists the read-only YOLO11 original as
  item 8. Both aligned.

Audited and deliberately left as they are: the seven Chinese-only `archive/legacy-notebooks/*.ipynb`
plus the four YOLO11 figures they embed (the English course never had these drafts; the archive READMEs
and `ONE_SIDED` say so), the `04-pretrained-{chinese,english}-sentiment` alias pair,
`english/02-object-detection/data/coco8/README.md` (English smoke-mode download, upstream text,
gitignored), the two byte-identical gitignored `01-image-classification/archive/data/DOWNLOAD.md`
provenance notes, and module `scripts/*.py` (parity pairs documents; the English generator lives in
`english/scripts/` and `02-object-detection/scripts/embed_expected_outputs.py` is only an entry shim for
the shared root script). Different heading counts in a few READMEs turned out to be folded sections,
not missing content. Three untracked `reference-*.png` files sit at the repository root, byte-identical
to the copies in `00-machine-learning/assets/`.

All seven checks green after the sweep: `verify_saved_outputs.py` (30 notebooks, 0 problems),
`check_docs_assets.py` (0 problems), `check_parity.py` (0 problems, 9 nested README pairs),
`check_course.py` (0 problems), `build_chinese_course.py --check` (11), `build_english_course.py --check`
(1), `git diff --check`. Committed as `750f381` together with Sessions 18 and 19; not pushed.

中文小结：把 `english/01|02|03` 与中文母本逐文件对了一遍。真正的缺漏有两处
`english/03-sentiment-analysis/outputs/{paddle,pytorch}/README.md`，根因是 `english/.gitignore` 的
`**/outputs/**` 缺少嵌套 README 例外，英文侧这类说明文件本来就进不了库；补齐文件并补齐例外规则。
`check_parity.py` 新增守卫：属于仓库的 `data/`、`outputs/` 内 README 也必须中英成对（用探针文件验证会报错、移除后恢复干净）。
另清掉 12 个文件里 16 处仍称"英文母本"的表述（01/03 模块 README 两侧 + 6 份 legacy README），统一成
"仓库规则=中文母本 + Migration status=这两模块生成器仍以英文文本为键"；英文视觉 legacy README 原本套的是 NLP 模板，
已按中文母本重写（归档原因、opt-in 重跑命令、逐本状态表、两处硬缺失）；`english/03/.../$d/` 模板占位符已修；
英文 01/03 README 补回指中文课程入口行，英文检测清单补上第 8 项只读原件。
七项校验全绿，与 Session 18/19 一并提交为 `750f381`（未推送）。

## Session 19 - the course direction turns around: Chinese is the master, English is derived

The user asked whether the "English-first, `english/` holds the masters" rule should simply be
deleted from the repository, or replaced with "Chinese is the master, English is derived".
A bare deletion would leave no direction at all while `check_parity.py` and both builders still
need one, so the second option was implemented: **the Chinese lessons are the masters and
`english/` holds derived mirrors**. Landed in commit `750f381` together with Session 18's work; not pushed.

What landed:

- `scripts/build_english_course.py`: a ZH -> EN mirror generator, deliberately symmetric with
  `scripts/build_chinese_course.py`. Markdown is keyed on the exact first line of the Chinese
  cell, code on the exact de-indented Chinese line; a cell or line containing Chinese that is not
  in the tables is a build error, and so is a translation the master no longer uses. It refuses to
  overwrite a mirror that already carries saved outputs unless `--force`.
- `scripts/titanic_en.py`: the 00 lesson's tables - 53 whole-cell markdown translations and
  206 line-level code translations (comments plus user-visible text). Keys were extracted from the
  master itself, and every pair was read back to confirm alignment.
- `english/00-machine-learning/`: the derived English notebook, a byte-identical copy of the
  Titanic CSVs (both READMEs publish the two SHA-256 values), an English `assets/README.md`, and a
  module `README.md` matching the one-README-per-side convention of the other modules. The
  Chinese side's redundant `README.zh-CN.md` (created in Session 18, never committed) moved to
  Trash: inside a module directory the repo keeps one `README.md` per side, and a Chinese file
  under `english/` would break `check_course.py`.
- `00-machine-learning/README.md` is now Chinese prose on the master side, states that it is the
  master, and documents the edit -> derive -> execute -> embed loop.
- `execute_and_save.py --group ml` follows `--language` instead of hard-coding the Chinese tree, so
  the same group runs either side. `check_parity.py` gained `00-machine-learning`, and
  `embed_expected_outputs.py` carries the English intro for the mirror.
- Direction documentation: `AGENTS.md` (new Project direction with an explicit **Migration status**
  list), both root READMEs (the module table now reads Chinese master / English mirror and gained
  the 00 row), both environment-setup guides, and the eleven "English (default)" front-door labels
  across the root, module and `docs/` guides, which now say master/mirror.

Execution of the English mirror (`--group ml --cwd module`, `env_dl_uv`, CPU, default parameters):
**passed, 85.02 s**, 98 code cells, 97 output items, 28 figures - the same shape as the Chinese
master's 84.82 s run, and the headline metrics agree cell for cell (SVM test 81.78% / CV 82.13%
with the defaults confirmed optimal, Pipeline best CV 82.18% and test 80.6%, XGBoost CV 82.38%,
LightGBM CV 82.71%). Embedding wrote 75 text blocks and 28 figures per side and left the Chinese
notebook byte-identical.

Checks after the change (repository root): `check_course.py` 0 problems over 97 course source files
and 16 notebooks - which is also the proof that the derived notebook kept no Chinese,
`check_parity.py` 0 problems with 00 included, `verify_saved_outputs.py` 0 problems,
`check_docs_assets.py` 0 problems, `build_chinese_course.py --check` 11 mirrors,
`build_english_course.py --check` clean, `git diff --check` clean. `tests/check-launcher.ps1`
still cannot run here (no `pwsh`); the launcher is untouched.

A follow-up sweep then removed the last wording that still claimed English was primary, because the
direction rule has to hold in the tooling and not just in the front door:
`scripts/build_chinese_course.py` no longer calls English "the only master" (its docstring now says
it is a transitional EN -> ZH generator for the eleven vision/NLP notebooks, and its missing-source
message says so too), `scripts/check_parity.py` dropped its "English side is the master" comment,
`01-image-classification/data/README.md` links to the "English mirror" guide instead of the "default
English" one, `docs/environment-setup.md` calls its own file the English mirror, `english/README.md`
now states that it is derived and that the Chinese course is the master, and
`english/docs/environment-setup.md` attributes "default" to the launcher rather than to the course.
All seven checks were re-run after those edits and are still green.

Deliberately **not** done, and worth a decision:

- `01-image-classification` and `03-sentiment-analysis` are still generated in the old direction by
  `scripts/build_chinese_course.py` (EN -> ZH, tables keyed on English text), and
  `english/02-object-detection/dataset-formats/` is still English-authored. AGENTS.md records this
  as Migration status instead of pretending the flip is already global. Reversing those two modules
  means re-keying a 529-line generator onto the Chinese side and can be proven equivalent by
  comparing the reverse-generated mirrors with the current English notebooks cell by cell.
- `start-notebooks.ps1` still defaults to `-Language en` / `vision`, because `tests/check-launcher.ps1`
  pins that routing and the default is a user-facing choice.
- `check_parity.py` now reports 81 English-only user-visible strings in the Chinese 00 master
  (plot titles and labels inherited from the original Kaggle notebook). It is a metric, not a
  failure, and it is the master's own text: localising it changes the master's outputs and both
  mirrors, so it is offered as follow-up work rather than done silently.

中文小结：按用户给的第二条路线翻转课程方向 - **中文课件为母本，`english/` 为派生镜像**（"English-first"
不再是仓库约定）。新增 `scripts/build_english_course.py`（与 `build_chinese_course.py` 对称的中 → 英
派生器，Markdown 按中文单元首行、代码按去缩进原行精确匹配，漏译与失效译文都直接报错）与
`scripts/titanic_en.py`（53 个整元 Markdown + 206 行代码译文，键取自母本原文并逐对回读校验）。
英文侧 `english/00-machine-learning/` 落地：派生课件、与母本 SHA-256 相同的数据副本（两侧 README 公布
哈希）、英文 `assets/README.md`、与其余模块一致的单份 `README.md`；母本侧多余的 `README.zh-CN.md`
（上一会话新建、未提交）已移入废纸篓，因为模块目录按约定每侧只有一份 README，且 `english/` 下不允许中文。
`--group ml` 改为跟随 `--language`，`check_parity.py` 纳入 00 模块。英文镜像实跑 **85.02 s 通过**，
98 单元 / 97 输出 / 28 图，关键指标与母本逐字一致；两侧各内嵌 75 文字块 + 28 图，母本逐字节不变。
文档翻转：`AGENTS.md` 新增「Migration status」如实标注视觉/NLP 仍是旧的英文 → 中文生成器、
dataset-formats 仍是英文母本，门面 11 处 "English (default)" 改为母本/镜像表述，启动器默认值与
`tests/check-launcher.ps1` 保持原样（改默认属另一决策）。视觉/NLP 反向重做、母本侧 81 处遗留英文图表
文案、启动器默认语言三项，留待用户定夺。收尾再扫了一遍仍在宣称英文为主的措辞，把
`scripts/build_chinese_course.py` 的「english/ 是唯一母本」改写成「过渡工具，视觉与 NLP 这 11 本的翻译来源暂时在英文侧」，
`scripts/check_parity.py` 去掉「英文侧是母本」注释，`01-image-classification/data/README.md`、
`docs/environment-setup.md`、`english/README.md`、`english/docs/environment-setup.md` 四处门面/镜像表述统一为
母本/镜像口径（启动器的"默认"只归因于启动器本身）。七项校验重跑全绿。改动与 Session 18/20 一并提交为 `750f381`（未推送）。

## Session 18 - the classical-ML Titanic lesson lands as `00-machine-learning/`

The user added a classical machine-learning module (Titanic survival prediction, Chinese prose,
from a Kaggle-style notebook) at the repository root and asked to execute it for real in the
course's uv workflow and quote the run back into the notebook like every other lesson. The user
first asked for a separate `~/env_ml_uv`, then changed direction mid-session: **share the existing
`~/env_dl_uv`**, and `env_ml_uv` was deleted (kernelspec removed, directory moved to Trash).

What landed:

- `00-machine-learning/` (Chinese course only, no English mirror; `check_parity.py` accepts it):
  `notebooks/01_Titanic-Case.ipynb`, data under `titanic/` (Kaggle LabeledData/UnlabeledData CSV,
  not in Git), bilingual module README pair, `assets/README.md` documenting the three unreferenced
  teaching-tool screenshots (renamed to `reference-1..3.png` to satisfy the `<name>-<N>` asset rule).
- `~/env_dl_uv/pyproject.toml` gained seaborn, scikit-learn 1.7.2, xgboost 3.4.1, lightgbm 4.7.0,
  skl2onnx 1.20.0, onnxruntime 1.31.0 (`uv sync` clean). The ML stack, the paddle/gensim stack and
  the torch/ultralytics stack each import fine in their own process, as every lesson kernel uses
  one stack; importing paddle and torch together in one process hits the known OMP conflict and is
  not something any course notebook does.
- Tooling: `execute_and_save.py` accepts `--group ml` (runtime-cell pin: scikit-learn 1.7.2) and a
  new `--cwd module` (kernel cwd = the module directory: the notebook lives in `notebooks/` but
  reads `titanic/` and writes `models/`/`result/` from the module root). `embed_expected_outputs.py`
  lists the module by default and carries its registered Chinese intro; `verify_saved_outputs.py`
  discovers `00-machine-learning/notebooks`.
- Lesson fixes needed to execute on a clean tree: the submission/model cells wrote to
  `result/`/`models/` that never existed - each writer now creates its directory first
  (`Path(Path.cwd(), 'result').mkdir(exist_ok=True)`; plain `Path('../result')` does **not**
  collapse `..`, which is what made the first two runs fail), and the Pipeline submission now
  writes `Submission_SVM_Pipeline.csv` where the prose says (the module directory). `.gitignore`
  excludes `models/`, `result/`, `*.pkl`, the submissions and `tmp.csv`.

Execution (`--group ml --language zh-CN --cwd module`, env_dl_uv, CPU, default parameters):
**passed, 84.82 s**, 98 code cells, 97 output items, 28 figures. Headline numbers quoted into the
intro: model table best SVM (10-fold CV 0.8146); GridSearchCV confirms SVM defaults are already
optimal (CV 82.13%, test 81.78%); Pipeline + GridSearchCV best CV 82.18% (test 80.6%);
XGBoost CV 82.38%; LightGBM CV 82.71%; the ONNX export re-scored by onnxruntime matches sklearn
predictions. `scripts/embed_expected_outputs.py --module 00-machine-learning` embedded 75 text
blocks and 28 figures into `notebooks/assets/01_Titanic-Case-<N>.png`; a second embed run leaves
the file byte-identical.

Checks after the change (all from the repository root): `verify_saved_outputs.py` 29 notebooks /
0 problems, `check_docs_assets.py` 0 problems, `check_parity.py` 40 notebooks / 0 problems,
`check_course.py` 0 problems, `build_chinese_course.py --check` 11 mirrors, `git diff --check`
clean. `tests/check-launcher.ps1` was not run this session (no `pwsh` on this host; the launcher
is untouched). Docs updated: both environment-setup guides (coverage, `--group ml`, `--cwd module`)
and the Chinese README module table. Untracked at the time of writing; committed later as `750f381`
together with Sessions 19 and 20.

中文小结：新增的泰坦尼克号经典机器学习课按课程既有流程落地为 `00-machine-learning/`（仅中文侧）。环境按用户
改定的方案并入课堂主环境 `~/env_dl_uv`（补 seaborn/scikit-learn/xgboost/lightgbm/skl2onnx/onnxruntime，
临时建的 `env_ml_uv` 已删除）。为能在干净仓库跑通，写出单元补了建目录逻辑（`Path('../x')` 不折叠 `..`
是前两次失败的根因，改用 `Path(Path.cwd(), x)`），Pipeline 提交文件按正文写回模块目录。`--group ml
--cwd module` 实跑通过（CPU，84.82 s，98 单元、28 图），真实结果内嵌 75 个「预期输出」块 + 28 张
`assets/` 图，重复内嵌逐字节幂等；四项目检 + 镜像校验 + diff 检查全部 0 问题。校验报告见
`english/reports/ml-zh-CN-executed.json`。

## Current user direction

The project is **Chinese-master-first**: the root-level Chinese lessons are the masters and `english/` holds derived mirrors (see Session 19 and Migration status in AGENTS.md). The user supplied the official `Rock-Paper-Scissors.v1i.yolo26.zip` and selected **YOLO26n** for both language lessons. The user explicitly stopped the earlier flattened VOC package workflow. Dataset conversion and Xiaotudui Labs viewer instructions must be a **separate parallel topic**, not part of model-training notebooks.

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

## Session 15 - the archived LeNet notebook is executed too, and quotes its own run

`01-image-classification/archive/01-lenet-mnist-copy1.ipynb` is now executed for real in `~/env_dl_uv`
(Python 3.12.12, torch 2.14.1, Apple MPS, `seed=42`, three classroom epochs on full MNIST, 37.22 s end to end,
best test accuracy **98.32%**, reloaded checkpoint 98.32%) and its real output is quoted back into the notebook:
13 `预期输出` blocks plus 6 figures at `archive/assets/01-lenet-mnist-copy1-1..6.png`, and a preface recording the
environment, the numbers and the refresh commands. Its cell 0 no longer claims the outputs are unverified history.
The English twin `english/01-image-classification/archive/01-lenet-mnist-copy1.ipynb` was re-executed as well
(5.03 s) and carries 7 `Expected output` blocks plus 2 English-labelled figures. Clearing all outputs was verified to
leave all 14 embedded blocks and all 6 figures visible.

Real defect fixed: that notebook resolves `../data`, `../outputs` and its own `assets/` from the notebook directory,
exactly as its header states, but the executor always ran notebooks from the course root, so section 10 silently
printed `Image not found: assets/lenet-7.jpg` and wrote data and weights into `/Users/will/workspace/` outside the
repository. `english/scripts/execute_and_save.py` gained an opt-in `--cwd root|notebook` (default `root`, every course
notebook unchanged); with `--cwd notebook` the single-image cell really predicts (`5` at 0.9959) and the checkpoints
land in `01-image-classification/outputs/lenet_mnist_standard/`.

`scripts/embed_expected_outputs.py` gained `--include-archive` (archive root notebooks only, `legacy-notebooks/` stays
out) and `--notebook` for targeted refreshes; kernel temp-directory paths in quoted warnings are folded like absolute
repository paths and get their own explanatory note; inserted cell ids are derived from block content, so re-embedding
is now byte-idempotent (verified by hashing two consecutive runs).

Verdict on `archive/legacy-notebooks/` (read-only history: not executed, not embedded, untouched):
`01-lenet-mnist.ipynb` looks runnable in `env_dl_uv` (all cells executed, imports present, MNIST local).
`02-lenet-cifar10.ipynb` and `extensions/04-lenet-custom-data.ipynb` still depend on `!cp -r /workspace/DataSet/cvdata/...`
copies, a `data/pipline_train` folder that does not exist here, and LEDNUM `train.txt`/`test.txt` with no public
download; `03-resnet-cifar10.ipynb` has 15 of 16 cells never executed and `extensions/04` keeps one saved error output.
The `!cp -r` lines are IPython shell magics, not syntax errors.

Also deleted `archive/assets/.ipynb_checkpoints/lenet-7-checkpoint.jpg` (byte-identical to `assets/lenet-7.jpg`,
left by a JupyterLab session), which was the only failing `check_docs_assets.py` problem.

Checks after the change: `verify_saved_outputs.py` 28 notebooks / 0 problems, `check_course.py` 95 sources / 0 problems,
`check_docs_assets.py` 0 problems, `check_parity.py` 0 problems, `build_chinese_course.py --check` 11 mirrors,
`git diff --check` clean. The previous session's uncommitted edits (kernelspec metadata on four lessons, plus two
legacy notebooks) were deliberately left untouched; `reports/parity-checks.json` still reports their cell counts
because the check runs over the working tree.

中文小结：归档的 Copy1 对照版已在 `~/env_dl_uv` 真跑（MPS、`seed=42`、全量 MNIST 3 轮、37.22 s、test 98.32%，
加载 checkpoint 复测一致），并把 13 个「预期输出」文字块与 6 张图内嵌回 notebook 本体，清空输出后仍可对照；
英文同名归档同步刷新。修掉一个真问题：这份 notebook 按开头约定以自身目录解析 `../data`、`../outputs`、`assets/`，
而执行器固定用仓库根，导致第 10 节实际只打印 `Image not found`，数据与权重还落到仓库外。执行器加 `--cwd notebook`，
内嵌脚本加 `--include-archive`、`--notebook`，内核临时目录绝对路径同样折叠并配准确注释，单元格 id 随内容稳定，
重复内嵌逐字节幂等。`legacy-notebooks/` 按只读约定未执行未内嵌，仅给出静态判定（外部数据、`pipline_train`、LEDNUM
缺失，03 有 15/16 单元从未执行，`!cp -r` 是 IPython 魔法不是语法错误）。清掉一个让 assets 检查失败的 Jupyter
遗留副本。六项校验全绿。

## Session 16 - every legacy vision lesson is executed in `env_dl_uv` and quotes its own run

Requested directly: run each notebook under `01-image-classification/archive/legacy-notebooks/` in the locked
environment and quote the result back **into the original notebook** (no copies). All four were executed with
`english/scripts/execute_and_save.py --group vision --language zh-CN --cwd notebook --include-legacy`
and quoted back with `scripts/embed_expected_outputs.py --include-archive --include-legacy`, in the foreground and
one at a time so MPS never runs two training jobs at once:

- `01-lenet-mnist.ipynb` — 66.73 s, full MNIST, three classroom epochs, best test **98.32%** (reloaded checkpoint
  98.32%), single image `lenet-7.jpg` predicts `5`; 14 text blocks plus 8 figures.
- `02-lenet-cifar10.ipynb` — 32.81 s, test 47.66% → 52.90% → **57.23%**, single image predicts 飞机 at 0.789;
  5 blocks plus 3 figures.
- `03-resnet-cifar10.ipynb` — **3897.96 s (about 65 minutes)** because this lesson resizes CIFAR-10 to 224×224 and
  trains twice (plain loop plus the "炫酷版" panel): loop test accuracy 91.65% → 92.08% → **93.68%**, the panel's
  second three-epoch run peaks at 91.91% while using the test set for selection, and `resnet-2.png` predicts `plane`;
  5 blocks plus 4 figures.
- `extensions/04-lenet-custom-data.ipynb` — 58.62 s on full MNIST: test 95.10% → 97.22% → **97.66%**, the panel's
  validation best 97.07%, `lenet-7.jpg` predicts `5` twice; 6 blocks plus 5 figures.

Two parts are deliberately **not** executed, and the notebooks say so instead of pretending to be verified. The last
cell of `03` loads `models/resnet18_cifar10/best_model/..._acc_93.05.pth`, a checkpoint trained on the old server that
never entered this repository, and section 三 of `extensions/04` needs the LEDNUM digit images, whose staging directory
only ever contained `DOWNLOAD.md` (`docs/datasets.zh-CN.md` records that there is no verifiable public download).
Those cells carry `skip-execution`, each section gained a note naming the missing asset and how to supply it, and
`README.md` in the legacy folder now tabulates per-notebook status, run times and refresh commands.

Restored teaching asset: `archive/assets/lenet/test_cifar10.png`, the input image of `02`, was missing. A pixel search
over CIFAR-10's test split shows it is **exactly test index 44 (label 0, airplane; next-best candidate MSE 2006)** and
pixel-identical to the module's own `assets/resnet-2.png`, which `03` predicts as `plane` - so the two lessons
cross-check the same image. `scripts/check_docs_assets.py` gained a documented `HISTORICAL_ASSET_DIRS` exception for
that one directory, because `docs/migration/file-map.json` records the historical `assets/lenet/<name>.png` layout that
the archived code reads; every other `assets/` directory still has to stay flat.

Tool changes needed to get here: both scripts accept `--include-legacy` (default stays "legacy is history"), `--notebook`
now matches repository-relative path fragments so a legacy lesson can be selected even when a current lesson shares its
file name, and embedded quotes strip ANSI colour codes - the "炫酷版" panels are coloured terminal output, and 589
escape sequences had leaked into the `01` appendix block before this session.

`archive/legacy-notebooks/` stays out of `verify_saved_outputs.py` either way, so delivered-course claims are still
verified only against delivered notebooks.

Checks after the change: `verify_saved_outputs.py` 28 notebooks / 0 problems, `check_course.py` 95 sources and
15 notebooks / 0 problems, `check_docs_assets.py` 0 problems (with the historical asset directory reported),
`check_parity.py` 0 problems, `build_chinese_course.py --check` 11 mirrors, `git diff --check` clean, and re-embedding
the whole module twice leaves identical bytes. The metadata-only churn a module-wide embed produces (derived cell ids
on lessons whose blocks predate that scheme, plus the kernelspec edits the previous session left uncommitted) is
recorded in the follow-up commit "vision lesson metadata is committed so embedding is a no-op", not in this one.

中文小结：按要求把 `legacy-notebooks/` 下四本历史中文课件在 `~/env_dl_uv` 里逐本真跑（前台、串行，避免两个训练抢 MPS），
并把真实输出内嵌回原 notebook：01（66.73 s，98.32%，14 块 8 图）、02（32.81 s，57.23%，飞机 0.789，5 块 3 图）、
03（3897.96 s≈65 分钟，224×224 且训两遍，loop test 93.68%、「炫酷版」validation 最佳 91.91%，单图 plane，5 块 4 图）、
extensions/04（58.62 s，MNIST test 97.66%、validation 最佳 97.07%、单图 5，6 块 5 图）。两处硬缺失不硬跑：03 末尾加载旧服务器
权重的单元、04 第三节 LEDNUM 整节，统一打 `skip-execution` 并在段首写清缺什么、怎么补，README 逐本记状态与刷新命令。
补回丢失素材 `archive/assets/lenet/test_cifar10.png`：在 CIFAR-10 test 集逐像素搜索确认它就是下标 44（label 0 airplane，
次优误差 2006），并与本模块 `assets/resnet-2.png` 像素一致，两课互为印证；`check_docs_assets.py` 为该目录加了一条有迁移记录
依据的 `HISTORICAL_ASSET_DIRS` 豁免，其余 assets 仍要求扁平命名。工具侧：两个脚本加 `--include-legacy`，`--notebook` 支持
仓库相对路径片段，内嵌摘录剥离 ANSI 颜色码（01 附录原先混入 589 个转义符）。六项校验全绿，重复内嵌逐字节幂等；越界改到
的课程 notebook（仅单元格 id 规范化）已回退，上一会话遗留的未提交改动未动，`main` 仍领先 `origin/main` 一个提交。

## Session 17 - vision lesson metadata is committed so embedding is a no-op

Nine notebooks carried uncommitted metadata only: `kernelspec.display_name` `Python 3` -> `Python 3 (ipykernel)` on
`01` Chinese and English, `language_info.version` 3.12.7 -> 3.12.12 on the YOLO11 original (a Jupyter save artifact of
opening that file in `~/env_dl_uv`; the lesson still never executes there and no course text claims otherwise), and
content-derived ids on the `course-expected-output` cells of the eight vision lessons whose blocks predated that id
scheme. A line-by-line check confirmed every changed line is an `"id"`, `display_name` or `version` field: no cell
source, no saved output and no asset moved.

Why commit instead of reverting again: `scripts/embed_expected_outputs.py` derives the ids of the cells it inserts from
block content, so while these ids stay uncommitted, running the documented embed command on a clean tree dirties nine
files every time. After this commit, re-embedding the vision module changes nothing.

Checks after the change: `verify_saved_outputs.py`, `check_course.py`, `check_docs_assets.py` and `check_parity.py` all
report 0 problems, `build_chinese_course.py --check` still validates 11 mirrors, `git diff --check` is clean, and a
second embed run leaves the tree identical.

中文小结：把 9 本 notebook 的纯元数据改动提交掉——三本 kernelspec 显示名改成 `Python 3 (ipykernel)`、YOLO11 原件的
`language_info.version` 记为 3.12.12（只是用 `~/env_dl_uv` 打开保存留下的痕迹，不代表那门课能在本环境运行，课程文案也没这么宣称），
八本视觉课件的「预期输出」单元格改用内容派生 id。逐行核对确认只动 `id`/`display_name`/`version`，代码、输出、图片零改动。
不提交的话，任何人按文档跑一次内嵌脚本都会脏 9 个文件；提交后视觉模块重复内嵌零 diff。六项校验全绿。
