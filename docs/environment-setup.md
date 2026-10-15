# 环境准备

图像分类、PyTorch NLP、Paddle NLP 使用三个独立环境。目标检测按外部工程说明另建环境。

## Windows 示例

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

环境验证后再生成并提交新的锁文件，记录 Python、框架、设备和验证日期。当前所有训练实验均处于未验证状态。
