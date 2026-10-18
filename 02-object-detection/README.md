# 目标检测：YOLO26

中文课程 · [English (default)](../english/02-object-detection/README.md) · [中文总览](../README.zh-CN.md)

中英文统一采用 **Ultralytics YOLO26n（yolo26n.pt）**，使用 [melikeavan / Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1) 正式 YOLO26 导出。训练 3,939 张、验证 338 张、测试 186 张；原编号为 `0=paper、1=rock、2=scissors`，已查看带框样本确认。

1. [CV 总览](lessons/01-cv-overview.md)
2. [CNN 基础](lessons/02-cnn-basics.md)
3. [YOLO26 理论](lessons/03-yolo-theory.md)
4. [YOLO26 实践](lessons/04-yolo-practice.md)
5. [石头剪刀布 YOLO26 Notebook](notebooks/01-yolo26-rock-paper-scissors.ipynb)

## 运行

中英文共用 `english/02-object-detection/` 下锁定的 uv 环境和只读数据。首次导入正式数据包，在仓库根目录运行：

```powershell
uv sync --locked --default-index https://pypi.org/simple --project .\english\02-object-detection
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\fetch_rps.py --archive C:/Users/will/Downloads/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
.\start-notebooks.ps1 -Language zh-CN -Module detection
```

已导入数据时无需再次导入，脚本拒绝合并或覆盖现有目录。选择检测环境内核，逐格执行。中文输出写入 `02-object-detection/outputs/`，英文输出写入 `english/02-object-detection/outputs/`。

默认 10 轮、320 像素。设置 `$env:COURSE_EPOCHS='1'` 可做全部正式训练数据的一轮实际运行与测试评估；`COURSE_SMOKE=1` 则改用 COCO8，只验证管线。两者不要混为默认十轮结果。

## 独立数据专题与历史内容

[VOC / COCO / YOLO 转换与小土堆查看器](../04-dataset-formats/README.zh-CN.md)是平行专题，训练直接读取 YOLO 导出。完整来源、许可、哈希、划分见[数据集指南](../docs/datasets.zh-CN.md)。

原 [PaddleYOLO / YOLO11 Notebook](notebooks/01-yolo11-rock-paper-scissors.ipynb) 与 [历史理论](archive/lessons/03-yolo-theory.md)、[历史叶病虫害实践](archive/lessons/04-yolo-practice.md)仅作对照；其中外部 PaddleDetection 工程、Linux 路径和旧配置不属于当前 YOLO26 启动流程。
