中文（母本） · [English mirror](environment-setup.md)

# 环境准备

全课只需要一个环境：**仓库根本身就是一个 uv 工程**（`pyproject.toml` + `uv.lock` + `.python-version`），在根目录 `uv sync` 一次就装齐图像分类、目标检测（含车流量统计）、数据格式专题、PyTorch NLP、Paddle NLP 与经典机器学习课，中英两侧共用同一个 `.venv`（见下方「一门课一个内核」）。模块目录不再各自保存 `pyproject.toml`、`uv.lock` 或 `requirements.txt`。中英文目标检测统一采用 YOLO26n，旧 PaddleYOLO 仅供历史对照。

## YOLO26 检测（中英文共用环境）

当前实跑环境为 Python 3.12.12、PyTorch 2.14.1、Ultralytics 8.4.177，中英文两侧使用同一个解释器；本机跑在 Apple 芯片的 MPS 后端上。依赖由仓库根的 `uv.lock` 锁定，Windows 上先在仓库根同步环境，再用启动器打开：

```powershell
uv sync --locked --default-index https://pypi.org/simple
.\start-notebooks.ps1 -Language zh-CN -Module detection
```

正式数据包导入见[数据说明](datasets.zh-CN.md)。中文与英文训练产物分开保存；实跑设备见[设备选择](#设备选择)，NVIDIA CUDA 尚未验证。

## 装好这一个环境

只需要 [uv](https://docs.astral.sh/uv/)，在仓库根目录执行一次（`.venv` 已被 `.gitignore` 排除，首次解析需要网络）：

```powershell
uv sync --locked --default-index https://pypi.org/simple   # Windows PowerShell
```

```bash
uv sync --locked                                          # macOS / Linux
```

之后用启动器打开任意模块的 JupyterLab：

```powershell
.\start-notebooks.ps1                                     # 英文 / 图像分类
.\start-notebooks.ps1 -Module pytorch
.\start-notebooks.ps1 -Module paddle
.\start-notebooks.ps1 -Module detection
.\start-notebooks.ps1 -Language zh-CN -Module vision      # 中文课程
.\start-notebooks.ps1 -DryRun                             # 只看路由，不装不启动
```

启动器在仓库根执行 `uv sync --locked`，再 `uv run jupyter lab --notebook-dir <模块>/notebooks`；PATH 上没有 uv 时退回 `python -m uv`。想在终端里直接用这个环境，在仓库内任意目录写 `uv run python …` 即可——uv 会自己向上找到仓库根的 `pyproject.toml`，不需要 `--project`。

Notebook 通过仓库根的 `CHINESE_COURSE_ROOT` 与 `english/COURSE_ROOT` 标记定位课程根目录，所以内核工作目录在模块 `notebooks/` 还是仓库根都能运行；迁移后的数据、图片和输出路径均按此约定设置，首次路径单元只建立数据与输出目录。

## 依赖状态

- 仓库根的 `pyproject.toml` 是唯一依赖清单，`uv.lock` 是唯一锁定结果，覆盖中英两侧全部模块以及 `scripts/`、`english/scripts/` 里的执行与校验脚本；模块级 `requirements.txt` 已随之取消。
- 版本对齐实跑验证过的那套环境：NumPy 1.26、PyTorch 2.14.1 / torchvision 0.29.1、PaddlePaddle 3.3.1、Ultralytics 8.4.177，以及泰坦尼克号课用到的 scikit-learn 1.7 与 XGBoost/LightGBM/skl2onnx/onnxruntime 栈。
- `uv.lock` 同时收录 macOS arm64、manylinux x86_64 与 Windows amd64 的 wheel。NVIDIA CUDA 仍需按本机驱动换成对应的 PyTorch 构建，先装框架再 `uv sync`；本轮没有安装或更改系统 Python 环境。
- 传递依赖与平台 GPU 包交由安装器解析，`tensorboard` 不在清单内（现行课程没有用到）。
- archive/environment/ 里保留的旧 `pyproject.toml`、`requirements.txt` 与锁文件只供追溯，不匹配当前依赖，不应复制回新环境。

改动依赖后在仓库根 `uv lock` 重新生成并提交锁文件，记录 Python、框架、设备和验证日期；YOLO26 结论以新检测执行报告为准。

## 一门课一个内核（全平台）

仓库根的 `.venv` 就是这唯一的一个解释器：`uv sync` 之后，图像分类、目标检测（含车流量统计 Notebook）、
数据格式专题、PyTorch NLP 轨道，以及经典机器学习课 `00-machine-learning/`（泰坦尼克号：CPU 侧的
scikit-learn/XGBoost/LightGBM 栈）都用它，中英两侧也是同一个：

```bash
cd /path/to/deep-learning-lab
uv sync --locked
uv run jupyter lab --notebook-dir english/01-image-classification/notebooks
```

`uv run` 启动的 JupyterLab 自带这个环境唯一的内核。如果要在别的 Jupyter 里选它，先注册一次：

```bash
uv run python -m ipykernel install --user --name deep-learning-lab --display-name deep-learning-lab
```

仓库外的 `~/env_dl_uv`（内核名 `env_dl_uv`）是本仓库现有全部「预期输出」与执行报告的实际运行环境，
依赖与 `uv.lock` 一致，保留作课堂机上的参照；新机器不需要它，用上面的 `.venv` 即可。英文 notebook
自行定位 `english/COURSE_ROOT`，中文 notebook 定位仓库根的 `CHINESE_COURSE_ROOT`，因此从仓库根目录或
`english/` 目录打开都能运行。

根清单同样刻意不装 `paddlenlp` 与 `visualdl`：它们锁定 `protobuf 3.20.x` 并面向 Paddle 2.x，会与实跑验证所用的
`paddlepaddle==3.3.1` 冲突。现行中文 Paddle 课程（`03-sentiment-analysis/paddle/notebooks/`）只用
`paddlepaddle` + `gensim`，在本环境可直接运行；需要 `paddlenlp`/ERNIE 的旧版本已归档在
`03-sentiment-analysis/paddle/archive/legacy-notebooks/`，请在独立的 Paddle 2.x 环境里查看运行。

## 设备选择

所有 PyTorch 课程用同一种顺序选择运算设备：先 CUDA，再 Apple 芯片的 MPS，最后 CPU。

```python
DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
```

两本检测 Notebook 把 `DEVICE` 保留为字符串，因为 Ultralytics 直接接收同样的三个取值
（`"cuda"`、`"mps"`、`"cpu"`）；预训练模型单元把同一个值传给 `pipeline(..., device=DEVICE)`。
Apple 芯片的 Mac 无需改代码即可用 MPS 训练，报告仍会写明实际运行设备。Paddle 课程保持
`paddle.set_device("gpu" if paddle.is_compiled_with_cuda() else "cpu")`，因为锁定的
`paddlepaddle==3.3.1` 没有 MPS 后端（`paddle.set_device("mps")` 会报错），macOS 上 Paddle 单元跑在 CPU。

Ultralytics 的训练入口在 `deterministic=True`（默认值）时会调用
`torch.use_deterministic_algorithms(True, warn_only=True)`。Apple 芯片上自动微分算子
`index_put_with_accumulate_mps` 没有确定性实现，这条告警每训练一轮重复一次，会把训练日志淹没，
因此两本检测 Notebook 把它静音，并把结论写清楚：MPS 上的重跑与保存成绩整体一致，
不保证逐位复现，小数第 3 位起可能出现差异。

## 执行与校验脚本

| 目的 | 命令（仓库根目录） |
|---|---|
| 整本执行并保留真实输出 | `uv run python english/scripts/execute_and_save.py --group vision\|pytorch\|paddle\|detection\|ml [--language zh-CN] [--notebook <名>] [--cwd root\|notebook\|module] [--include-legacy]` |
| 把实跑结果写回 notebook（`预期输出` + `assets` 图片） | `uv run python scripts/embed_expected_outputs.py [--module <模块>] [--notebook <名>] [--include-archive] [--include-legacy]` |
| 由中文母本派生英文镜像 | `uv run python scripts/build_english_course.py [--check] [--force]` |
| 重新生成中文镜像（视觉/NLP，暂时仍是英文 → 中文） | `uv run python scripts/build_chinese_course.py` |
| 中文检测课文案本地化 | `uv run python scripts/localize_chinese_detection.py` |
| 中英对齐与输出语言检查 | `uv run python scripts/check_parity.py` |
| 英文课程静态检查（禁止 `english/` 出现中文） | `uv run python english/scripts/check_course.py` |
| 全仓文档链接、图片本地化与 `assets` 命名检查 | `uv run python scripts/check_docs_assets.py` |
| 已保存输出与代码一致性 | `uv run python english/scripts/verify_saved_outputs.py` |

设置 `COURSE_SMOKE=1` 会把实验换成流程检查（检测用 COCO8、ResNet 用随机权重），其分数不代表模型质量；
`COURSE_EPOCHS=<n>` 同理，报告里必须写明运行配置。

课程 notebook 一律用仓库根目录作为工作目录（`--cwd root`，默认值）；`01-image-classification/archive/` 下那份
Copy1 对照版按它自己开头写明的约定，用 `--cwd notebook` 以 notebook 所在目录运行，这样 `../data`、`../outputs`
落在 `01-image-classification/`、`assets/` 落在 `archive/`。归档课件的「预期输出」需要 `--include-archive`
才会内嵌。`archive/legacy-notebooks/` 里重构前的课件默认不参与课程执行与产出校验；加 `--include-legacy`
会按同样的 `--cwd notebook` 约定把它们整本实跑，再用 `scripts/embed_expected_outputs.py --include-legacy`
把结果内嵌回去，只有依赖仓库外资产、带 `skip-execution` 标签的单元除外。

`00-machine-learning` 课件放在 `<模块>/notebooks/`，但按**模块目录**读写 `titanic/`、`models/`、`result/`，
所以必须用 `--cwd module`。这门课中英两侧都有，`--group ml` 跟着 `--language` 走：
`--language zh-CN --cwd module` 跑中文母本，省掉 `--language` 就跑 `english/` 下的英文镜像。
`scripts/build_english_course.py --force` 会清掉英文镜像的已保存输出，之后按「派生 → 执行 → 内嵌」的顺序刷新。
