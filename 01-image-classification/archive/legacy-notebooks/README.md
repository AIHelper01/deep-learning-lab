# 遗留中文 notebook（历史归档）

这里保存的是本仓库早期的中文 notebook，模块为「视觉分类」。归档原因：

- 结构与重构后的课程 notebook 不一致，无法逐单元对齐；
- 目录约定与课程 notebook 不同：它们按自身所在目录解析 `../data`、`../outputs`、`../../assets`，
  而课程 notebook 以课程根目录为工作目录；
- 部分单元依赖仓库外的旧服务器资产（见下）。

现行中文课程位于 `01-image-classification/notebooks/`，与英文侧同名课程一一对应（由 `scripts/check_parity.py` 校验）。
两侧目前以哪一侧充当翻译来源，见仓库根目录 `AGENTS.md` 的 Migration status。

## 在锁定环境里实跑（opt-in）

本目录默认不参与课程执行，也不参与 `english/scripts/verify_saved_outputs.py` 的产出校验；
需要复现时用 `--include-legacy` 显式打开，并配合 `--cwd notebook`（仓库根目录执行）：

```bash
~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group vision --language zh-CN \
    --cwd notebook --include-legacy --notebook legacy-notebooks/02-lenet-cifar10.ipynb
~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 01-image-classification \
    --include-archive --include-legacy --notebook legacy-notebooks/02-lenet-cifar10.ipynb
```

跑完紧接着内嵌，每个代码单元后面会多出一个带 `course-expected-output` 标签的 markdown 单元：
文字输出逐字摘录，图片导出到本目录 `assets/`（文件名主干 + 序号）并以相对路径引用，
所以 **Kernel → Clear All Outputs** 之后仍然看得见这次实跑的结果。

## 逐本状态（2026-10-19，`~/env_dl_uv`：Python 3.12.12 + PyTorch 2.14.1，Apple 芯片 MPS）

| Notebook | 状态 | 说明 |
| --- | --- | --- |
| `01-lenet-mnist.ipynb` | 已实跑并内嵌 | 全量 MNIST、3 轮，66.73 s，最佳 test 98.32%，单图预测 5 |
| `02-lenet-cifar10.ipynb` | 已实跑并内嵌 | CIFAR-10、3 轮，32.81 s，test 57.23%，单图预测飞机 0.789 |
| `03-resnet-cifar10.ipynb` | 已实跑并内嵌 | ResNet18（ImageNet 预训练）+ CIFAR-10、224×224、3 轮，3897.96 s，test 93.68%（「炫酷版」再训 3 轮，validation 最佳 91.91%）；末尾加载旧服务器权重的单元已跳过 |
| `extensions/04-lenet-custom-data.ipynb` | 第一、二节已实跑并内嵌 | 全量 MNIST、3 轮，58.62 s，test 97.66%（「炫酷版」validation 最佳 97.07%），单图预测 5；第三节「训练自己的数据」因缺少 LEDNUM 数据整体跳过 |

两处跳过都是硬缺失，不是环境没配好：

- `03-resnet-cifar10.ipynb`「炫酷版本」末尾加载
  `models/resnet18_cifar10/best_model/..._acc_93.05.pth`，那套权重在旧服务器上训练、从未入库，仓库与素材目录里都没有；
- `extensions/04-lenet-custom-data.ipynb` 第三节需要 LED 数字图片 `../../data/LEDNUM/`，
  旧机器上那份只剩 `DOWNLOAD.md`，也没有可核实的公开下载地址（见 `docs/datasets.zh-CN.md`）。
  同一套「自建 Dataset + `train.txt` 索引」做法，现行课程在
  `../../notebooks/extensions/04-lenet-custom-data.ipynb` 用可下载的 `data/custom-digits-balanced` 演示。

补到数据之后，按上面的命令重跑即可去掉跳过标记；被跳过的单元带 `skip-execution` 标签，执行器会原样跳过。

需要查看它们的历史改动，使用 `git log --follow <文件路径>`。
