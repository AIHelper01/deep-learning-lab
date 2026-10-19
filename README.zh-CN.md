# 深度学习实验室（中文课程）

中文课程（母本） · [English mirror](README.md)

中文课程与英文课程**逐单元一一对应**：同样的实验与训练逻辑，中文讲解、中文输出、中文图表，语言相关的环节直接用中文数据（NLP 用 ChnSentiCorp 中文评论 + jieba 分词，不是把英文 IMDb 翻译一遍）。

全课只有一个环境：**uv 工程就放在仓库根**（`pyproject.toml` + `uv.lock` + `.python-version`）。在根目录跑一次 `uv sync`，生成的 `.venv` 就是四个模块、中英两侧共用的内核（依赖 `paddlenlp`/`visualdl` 的历史 Paddle Notebook 除外），见[环境准备](docs/environment-setup.zh-CN.md)。PowerShell 里 `./start-notebooks.ps1 -Language zh-CN -Module vision` 会先同步环境再打开 JupyterLab。

命令行执行并保留真实输出：

```bash
uv sync                                          # 仓库根跑一次，装齐全部模块
uv run python english/scripts/execute_and_save.py --group vision --language zh-CN
uv run python scripts/embed_expected_outputs.py      # 把实跑结果写回 notebook（预期输出 + assets 图片）
uv run python scripts/check_parity.py                # 中英对齐与输出语言检查
uv run python scripts/check_docs_assets.py           # 全仓链接、图片本地化与 assets 命名检查
uv run python english/scripts/verify_saved_outputs.py # 中英两侧 28 本 notebook 的输出一致性
```

围绕经典机器学习、图像分类、目标检测与中文情感分析的 Notebook 教学项目。**根目录的中文课件是母本**，`english/` 下的英文课件由 `scripts/build_english_course.py` 逐单元派生。

| 模块 | 入口 | 内容 |
|---|---|---|
| 00 机器学习 | [课程说明](00-machine-learning/README.md) | 泰坦尼克号生存预测：EDA → 六种分类器 + XGBoost/LightGBM → 超参寻优 → 模型保存与 Pipeline |
| 01 图像分类 | [课程说明](01-image-classification/README.md) | MNIST → CIFAR-10 → ResNet → 自定义数据 |
| 02 目标检测 | [课程说明](02-object-detection/README.md) | CV 与 CNN 基础 → YOLO → 剪刀石头布检测 → 车流量统计 |
| 03 情感分析 | [课程说明](03-sentiment-analysis/README.md) | NLP → 词向量 → LSTM，Paddle/PyTorch 两条路线 |

首次学习从 [MNIST 规范版](01-image-classification/notebooks/01-lenet-mnist.ipynb) 开始。完成基础训练流程后，可以分别进入目标检测或情感分析。

- [学习路线](docs/learning-path.zh-CN.md)
- [环境准备](docs/environment-setup.zh-CN.md)
- [数据获取与放置路径](docs/datasets.zh-CN.md)
- [目录整理记录](docs/migration/reorganization.md)

依赖只在仓库根声明并锁定一次，模块目录不再各自保存 `pyproject.toml`、`uv.lock` 或 `requirements.txt`；仓库外的 `~/env_dl_uv` 只是课堂机上版本一致的参照环境。运行时的
工作目录是 Notebook 所在目录；数据放在各模块 `data/`，训练产物放在 `outputs/`，讲解图片放在 `assets/`。

## 数据：先放暂存区，再拷进模块

数据集不进 Git。课堂镜像是一个 DataSet 暂存目录（课堂机器上是 `/workspace/DataSet`，按 `yolo/`、`cvdata/`、`nlp/` 等
分子目录），各模块真正读取的数据在自己的 `data/` 下。每个模块的 `data/README.md` 都对每个数据集写清两条路径：
**cp 方式**（把暂存区的压缩包或已解压目录拷进模块，或交给模块的导入器）与**下载方式**（来源页、要选什么格式、压缩包
存到哪里）。

| 暂存位置 | 模块内位置 |
|---|---|
| `/workspace/DataSet/cvdata/MNIST`、`.../CIFAR10` | `01-image-classification/data/`、`english/01-image-classification/data/` |
| `/workspace/DataSet/yolo/*.zip` | 导入到 `english/02-object-detection/data/`（中英文共用的只读数据） |
| `/workspace/DataSet/nlp/imdb`、`.../ChnSentiCorp` | `03-sentiment-analysis/data/`、`english/03-sentiment-analysis/data/` |

当前状态（2026-10-19）：全部目录与文件名均为英文；依赖与内核收编到仓库根的 uv 工程，`uv sync` 之后 Jupyter 只有根 `.venv` 这一个内核；中文课程的 14 本
现行 Notebook（经典机器学习 1、图像分类 4、目标检测 2、PyTorch NLP 4、Paddle NLP 3）全部在课堂机上真实执行完毕，并把真实
结果内嵌为「预期输出」文字块与 `assets/` 图片，清掉输出后仍可对照。四项校验
（`check_parity.py`、`english/scripts/check_course.py`、`scripts/check_docs_assets.py`、
`english/scripts/verify_saved_outputs.py`）当前均为 0 问题；`check_docs_assets.py` 现在还检查链接锚点、`data/README.md`，
以及现行课件是否还在教人用已经淘汰的解释器命令或内核。
设备选择统一为 CUDA → MPS → CPU，本机实跑走 MPS。数据集现状：MNIST、CIFAR-10、石头剪刀布 v1、车辆计数 v4、COCO8 已落地到各模块
`data/`（`data/` 被 Git 忽略，缺失时按每个 `data/README.md` 里的 cp 方式或下载方式补齐）；检测两本中文 Notebook
已在 Apple 芯片 MPS 上按课堂默认轮数实跑完毕，与英文版同参数同种子成绩一致；中英文两侧的车流量 Notebook 共用同一份
v4 数据，各自执行并写入自己的 `outputs/`。全部实跑数字与运行配置见[执行证据](english/reports/README.md)与
[车流量实跑报告](02-object-detection/lessons/05-vehicle-counting-run-report.md)。


## 数据集格式与查看专题

[VOC / COCO / YOLO 转换与小土堆 Labs 查看](02-object-detection/dataset-formats/README.md)独立于模型训练课程。
