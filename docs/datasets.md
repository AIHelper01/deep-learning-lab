# 数据获取与放置路径

本仓库不提交任何数据集文件。下表列出每个数据集的来源、自动获取方式和落地目录；请自行下载后再运行 Notebook。
英文版的等价说明见 [english/docs/datasets.md](../english/docs/datasets.md)。

| 数据集 | 使用位置 | 获取地址 | 放置路径 |
|---|---|---|---|
| MNIST | 中文 01 图像分类 `01-lenet-mnist.ipynb`、`extensions/04-lenet-custom-data.ipynb` | `torchvision.datasets.MNIST(download=True)` 自动下载，官方源 <https://yann.lecun.com/exdb/mnist/> | `01-image-classification/data/MNIST/` |
| CIFAR-10 | 中文 01 图像分类 `02-lenet-cifar10.ipynb`、`03-resnet-cifar10.ipynb` | `torchvision.datasets.CIFAR10(download=True)`；离线可用官方包 <https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz> 或镜像 <https://huggingface.co/datasets/uoft-cs/cifar10> | `01-image-classification/data/CIFAR10/` |
| 剪刀石头布检测数据 | 中文 02 目标检测 `01-yolo11-rock-paper-scissors.ipynb` | Roboflow 目标检测导出 <https://universe.roboflow.com/roboflow-58fyf/rock-paper-scissors-sxsw>（需免费账号），或免凭证 CC BY 4.0 镜像 <https://huggingface.co/datasets/Xuban/rock-paper-scissors-roboflow> | 解压到 PaddleYOLO 工作区的 `dataset/Rock-Paper-Scissors/`，再按 Notebook 转 VOC/COCO |
| ChnSentiCorp | 中文 03 情感分析 Paddle 与 PyTorch 两条路线 | <https://bj.bcebos.com/paddlenlp/datasets/ChnSentiCorp.zip>，Notebook 中 `get_path_from_url` / `urllib.request.urlretrieve` 自动下载并解压 | `03-sentiment-analysis/data/ChnSentiCorp.zip` 与解压后的 `03-sentiment-analysis/data/ChnSentiCorp/` |
| IMDb 英文评论 | 英文 03 情感分析 | <https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz>，由 `english/common/course_data.py` 下载并转成 JSONL | `english/03-sentiment-analysis/data/imdb/` |
| 剪刀石头布（英文版） | 英文 02 目标检测正式实验 | 在 `english` 目录执行 `02-object-detection\.venv\Scripts\python.exe scripts\fetch_rps.py`，取免凭证 CC BY 4.0 镜像 <https://huggingface.co/datasets/Xuban/rock-paper-scissors-roboflow> | `english/02-object-detection/data/rps-mirror/`（缓存）与 `english/02-object-detection/data/rock-paper-scissors/`（课程导出） |
| COCO8 | 英文 02 目标检测的 `COURSE_SMOKE=1` 管线检查 | `english/common/detection_data.py` 自动下载 <https://ultralytics.com/assets/coco8.zip> | `english/02-object-detection/data/coco8/` |
| 预训练权重与模型 | 01 ResNet、02 YOLO、03 DistilBERT | torchvision、Ultralytics、Hugging Face 首次运行时自动下载 | 英文版缓存：`english/data/torch-cache/`、`english/data/huggingface/`、`english/02-object-detection/outputs/weights/` |

分发课程包时只发源码与文档，数据由学员按上表获取；`MNIST` 是唯一已经随本地环境解压存在的历史数据，同样不入库。各模块的 `data/README.md` 也重复了本模块的下载地址与落地路径，方便就地查看。
