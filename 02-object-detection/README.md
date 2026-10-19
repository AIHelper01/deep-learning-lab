# 目标检测：YOLO26

中文课程（母本） · [English mirror](../english/02-object-detection/README.md) · [中文总览](../README.zh-CN.md)

中英文统一采用 **Ultralytics YOLO26n（yolo26n.pt）**，使用 [melikeavan / Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1) 正式 YOLO26 导出。训练 3,939 张、验证 338 张、测试 186 张；原编号为 `0=paper、1=rock、2=scissors`，已查看带框样本确认。

1. [CV 总览](lessons/01-cv-overview.md)
2. [CNN 基础](lessons/02-cnn-basics.md)
3. [YOLO26 理论](lessons/03-yolo-theory.md)
4. [YOLO26 实践](lessons/04-yolo-practice.md)
5. [石头剪刀布 YOLO26 Notebook](notebooks/01-yolo26-rock-paper-scissors.ipynb)
6. [车流量统计 Notebook](notebooks/02-yolo26-vehicle-counting.ipynb)
7. [车流量统计实跑报告](lessons/05-vehicle-counting-run-report.md)（含全部真实输出与图片）
8. [原 PaddleYOLO / YOLO11 石头剪刀布 Notebook](notebooks/01-yolo11-rock-paper-scissors.ipynb)（课程早期原件，只读对照，不参与执行）

## 运行

中英文共用同一套依赖与同一份只读数据。课堂机器使用仓库外的单一环境 `~/env_dl_uv`（Jupyter 内核名 `env_dl_uv`）；也可以在 Windows 上把依赖锁定到检测模块。首次导入正式数据包，在仓库根目录运行：

```bash
# 课堂机器（macOS/Linux）：先按 data/README.md 把压缩包放进 DataSet 暂存区，再导入
~/env_dl_uv/.venv/bin/python english/scripts/fetch_rps.py \
  --archive /workspace/DataSet/yolo/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```

Windows 上先 `uv sync --locked --project english/02-object-detection`，再用启动器打开 JupyterLab：

```powershell
uv sync --locked --default-index https://pypi.org/simple --project .\english\02-object-detection
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\fetch_rps.py --archive C:/Users/will/Downloads/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
.\start-notebooks.ps1 -Language zh-CN -Module detection
```

已导入数据时无需再次导入，脚本拒绝合并或覆盖现有目录。选择检测环境内核，逐格执行。中文输出写入 `02-object-detection/outputs/`，英文输出写入 `english/02-object-detection/outputs/`。

手势实验与车流量实验共用同一个内核，环境细节见[环境准备](../docs/environment-setup.zh-CN.md)。

手势实验默认 10 轮、320 像素；车流量实验默认 5 轮、320 像素（数据大一个数量级）。设置 `COURSE_EPOCHS=1` 可做全部正式训练数据的一轮实际运行与测试评估；`COURSE_SMOKE=1` 则改用 COCO8，只验证管线。两者不要混为默认轮数的结果。

保存的实跑结果来自 Apple Silicon Mac 上的 MPS 设备，NVIDIA CUDA 尚未验证。Ultralytics 会用 `seed=42`
打开「仅告警」的确定性开关，但 MPS 上的自动微分算子 `index_put_with_accumulate_mps` 没有确定性实现，
因此重跑与记录成绩只在整体上一致，不保证逐位复现。

两个 Notebook 的每个代码单元后面都跟着一个「预期输出」单元：文字输出逐字摘录，图片导出到 `assets/` 并以相对路径引用，因此执行 **Kernel → Clear All Outputs** 之后真实结果仍然看得见，重跑后两者应当一致。输出变了就在仓库根目录刷新：`~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 02-object-detection`。

## 车流量统计案例

[车流量统计 Notebook](notebooks/02-yolo26-vehicle-counting.ipynb) 使用 [vehicle-counting-rtvul / vehicle-counting-tksu5 v4](https://universe.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/dataset/4)（CC BY 4.0，5 类车辆），从检测计数走到“跟踪 + 过线判定”的车流量统计。数据集统一存放在仓库外的 DataSet 暂存区（课堂镜像 `/workspace/DataSet/yolo`），导入到 `english/02-object-detection/data/`，与手势数据同目录约定，中英文共用只读数据。

完整实跑结果（真实训练与跟踪输出、逐单元预期输出、图片）见[车流量统计实跑报告](lessons/05-vehicle-counting-run-report.md)。

```bash
# 课堂机器（macOS/Linux），仓库根目录
~/env_dl_uv/.venv/bin/python english/scripts/import_vehicle_counting.py --from-staging
```

Windows 上先 `uv sync --project english/02-object-detection`：

```powershell
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\import_vehicle_counting.py --from-staging
```

跟踪依赖 `lapx`（提供 `lap` 模块）已在检测锁定环境中；`COURSE_SMOKE=1` 时视频链路仍可用，但模型不是车辆微调权重，计数仅供链路检查。默认演示视频是由数据集真实车辆裁剪合成的短片（每辆车只过一次线，有确定答案），设置 `TRAFFIC_VIDEO=/path/to/你的道路视频.mp4`（Windows 用 `$env:TRAFFIC_VIDEO`）可换成真实视频。计数实现见 `english/common/traffic_counting.py`。

## 独立数据专题与历史内容

[VOC / COCO / YOLO 转换与小土堆查看器](dataset-formats/README.md)是平行专题，训练直接读取 YOLO 导出。完整来源、许可、哈希、划分见[数据集指南](../docs/datasets.zh-CN.md)。

原 [PaddleYOLO / YOLO11 Notebook](notebooks/01-yolo11-rock-paper-scissors.ipynb) 保留在 `notebooks/` 里作为课程原件对照，它依赖仓库外的 PaddleYOLO 工程（`yolo11_*_600e_coco.yml` 等配置、Linux 路径与旧数据包），因此只读、从不执行，也不参与中英配对：`scripts/check_parity.py` 的 `HISTORY_IN_NOTEBOOKS` 与 `ONE_SIDED` 记录了这一处理，`english/scripts/execute_and_save.py` 与 `english/scripts/verify_saved_outputs.py` 都把它排除在执行与产出校验之外。[历史理论](archive/lessons/03-yolo-theory.md)与[历史叶病虫害实践](archive/lessons/04-yolo-practice.md)仍在 `archive/lessons/`。
