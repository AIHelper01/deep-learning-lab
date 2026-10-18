# 深度学习学习项目

从 AI Showcase 提取的三个独立学习模块。原仓库保留不变。

- [2.1深度学习-ImageClassification](2.1深度学习-ImageClassification/)
- [2.2深度学习-ObjectDetection](2.2深度学习-ObjectDetection/)
- [2.3深度学习-SentimentAnalysis](2.3深度学习-SentimentAnalysis/)

## 使用

各模块使用独立 Python 环境，不要合并安装依赖。在 Notebook 所在目录启动 Jupyter，保持相对路径有效。2.1 和 2.3 保留各自 requirements.txt、pyproject.toml、uv.lock；2.2 按教程准备 PaddleYOLO/PaddleDetection 环境。

Notebook 的中文说明、代码及历史输出均保留。名称含 Copy1 的 Notebook 内容与规范版不同，因此保留。已有 MNIST 解压数据已保留，首次运行其他数据集或预训练模型仍可能联网下载。在线图片保留原链接，未离线下载。

Paddle 版情感分析需要 paddlenlp>=2.6,<3.0。依赖文件沿用原项目，未安装依赖或执行训练；其中平台相关依赖需要结合操作系统与 GPU 环境选择。

详见 [迁移说明](migration-notes.md) 和 [文件清单](migration-manifest.json)。
