[English (default)](environment-setup.md) · 中文

# 环境准备

课程推荐一个内核跑通全部模块：仓库外的单个 uv 项目 `~/env_dl_uv`（见下方「一门课一个内核」）。图像分类、PyTorch NLP、Paddle NLP 与目标检测都在该环境里实跑验证；各模块的 `pyproject.toml` 与 `uv.lock` 仍随仓库保留，需要时可用 uv 重建独立环境。中英文目标检测统一采用 YOLO26n，旧 PaddleYOLO 仅供历史对照。

## YOLO26 检测（中英文共用环境）

当前实跑环境为 Python 3.12.12、PyTorch 2.14.1、Ultralytics 8.4.177，中英文两侧使用同一个解释器；本机跑在 Apple 芯片的 MPS 后端上。若要把依赖锁定到检测模块，可在仓库根目录用 PowerShell 重建模块环境：

```powershell
uv sync --locked --default-index https://pypi.org/simple --project .\english\02-object-detection
.\start-notebooks.ps1 -Language zh-CN -Module detection
```

正式数据包导入见[数据说明](datasets.zh-CN.md)。中文与英文训练产物分开保存；实跑设备见[设备选择](#设备选择)，NVIDIA CUDA 尚未验证。

## 原中文分类与 NLP 的 Windows 示例

在选定环境目录运行（01-image-classification、03-sentiment-analysis/pytorch 或 03-sentiment-analysis/paddle）：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m jupyterlab
```

请先确认 python 指向所需解释器。图像分类与 PyTorch NLP 的版本提示为 3.12，Paddle 的版本提示为 3.10；这些是准备环境的起点，尚未验证安装成功。也可使用 uv sync 解析 pyproject.toml，但当前未生成新 uv.lock，首次解析需要网络。

在 JupyterLab 中打开实验；内核工作目录应为该 Notebook 所在目录。迁移后的数据、图片和输出路径均按此约定设置。首次路径单元只建立数据与输出目录。

## 依赖状态

- 新 pyproject.toml 与 requirements.txt 列出代码直接需要的库；两份内容应同步维护。
- 图像分类使用原有 torch/torchvision 版本，去掉手工枚举的传递依赖与平台 GPU 包，交由安装器解析。
- PyTorch NLP 补列 torch、transformers 与 tensorboard。
- Paddle 保留原框架版本，将 NumPy 约束到 2 以下作为旧框架环境的候选方案；是否解决兼容问题需实际验证。
- GPU 安装应按本机驱动和所选框架确定软件源。本轮没有安装或更改系统 Python 环境。
- archive/environment/ 中的旧锁文件仅供追溯，不匹配新依赖，不应复制回新环境。

环境验证后再生成并提交新的锁文件，记录 Python、框架、设备和验证日期。本节原分类/NLP 环境的运行验证仍不完整；YOLO26 以新检测执行报告为准。

## 一门课一个内核（macOS/Linux）

`~/env_dl_uv` 是仓库外的单个 uv 项目，把四个模块的锁定依赖合并成一个解释器，本机只需要一个名为
`env_dl_uv` 的 Jupyter 内核即可跑通图像分类、目标检测（含车流量统计 Notebook）、数据格式专题和
PyTorch NLP 轨道：

```bash
cd ~/env_dl_uv
uv sync
.venv/bin/python -m ipykernel install --user --name env_dl_uv --display-name env_dl_uv
uv run --no-sync jupyter lab /path/to/deep-learning-lab
```

在 JupyterLab 中选 **env_dl_uv** 内核（Notebook → Change Kernel）。同一解释器还注册了等价的
`python3` 内核，命令行执行器用的就是它。英文 notebook 自行定位 `english/COURSE_ROOT`，中文 notebook
定位仓库根的 `CHINESE_COURSE_ROOT`，因此从仓库根目录或 `english/` 目录打开都能运行。

该环境刻意不装 `paddlenlp` 与 `visualdl`：它们锁定 `protobuf 3.20.x` 并面向 Paddle 2.x，会与实跑验证所用的
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
| 整本执行并保留真实输出 | `~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group vision\|pytorch\|paddle\|detection [--language zh-CN] [--notebook <名>] [--cwd root\|notebook] [--include-legacy]` |
| 把实跑结果写回 notebook（`预期输出` + `assets` 图片） | `~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py [--module <模块>] [--notebook <名>] [--include-archive] [--include-legacy]` |
| 由英文母本生成中文镜像 | `~/env_dl_uv/.venv/bin/python scripts/build_chinese_course.py` |
| 中文检测课文案本地化 | `~/env_dl_uv/.venv/bin/python scripts/localize_chinese_detection.py` |
| 中英对齐与输出语言检查 | `~/env_dl_uv/.venv/bin/python scripts/check_parity.py` |
| 英文课程静态检查（禁止 `english/` 出现中文） | `~/env_dl_uv/.venv/bin/python english/scripts/check_course.py` |
| 全仓文档链接、图片本地化与 `assets` 命名检查 | `~/env_dl_uv/.venv/bin/python scripts/check_docs_assets.py` |
| 已保存输出与代码一致性 | `~/env_dl_uv/.venv/bin/python english/scripts/verify_saved_outputs.py` |

设置 `COURSE_SMOKE=1` 会把实验换成流程检查（检测用 COCO8、ResNet 用随机权重），其分数不代表模型质量；
`COURSE_EPOCHS=<n>` 同理，报告里必须写明运行配置。

课程 notebook 一律用仓库根目录作为工作目录（`--cwd root`，默认值）；`01-image-classification/archive/` 下那份
Copy1 对照版按它自己开头写明的约定，用 `--cwd notebook` 以 notebook 所在目录运行，这样 `../data`、`../outputs`
落在 `01-image-classification/`、`assets/` 落在 `archive/`。归档课件的「预期输出」需要 `--include-archive`
才会内嵌。`archive/legacy-notebooks/` 里重构前的课件默认不参与课程执行与产出校验；加 `--include-legacy`
会按同样的 `--cwd notebook` 约定把它们整本实跑，再用 `scripts/embed_expected_outputs.py --include-legacy`
把结果内嵌回去，只有依赖仓库外资产、带 `skip-execution` 标签的单元除外。
