# 图像分类数据

| 数据 | 获取地址 | 落地路径 |
|---|---|---|
| MNIST | `torchvision.datasets.MNIST(download=True)`，官方源 <https://yann.lecun.com/exdb/mnist/> | `data/MNIST/` |
| CIFAR-10 | `torchvision.datasets.CIFAR10(download=True)`；离线包 <https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz>；镜像 <https://huggingface.co/datasets/uoft-cs/cifar10> | `data/CIFAR10/` |
| 自定义手写数字 | `extensions/04-lenet-custom-data.ipynb` 由本地 MNIST 生成，无需额外下载 | `data/custom-digits-balanced/` |

数据体积大，`.gitignore` 已排除 `data/` 下除本文件外的全部内容。离线环境请先按上面的地址下载并放到对应目录，Notebook 检测到本地数据后会直接复用。
