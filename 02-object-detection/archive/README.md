# 目标检测归档

只保留历史材料用于溯源，这里的内容都不属于当前 YOLO26 主线，请运行 `../notebooks/` 里的实验。

| 文件 | 是什么 | 为什么保留 |
|---|---|---|
| `lessons/03-yolo-theory.md` | 旧 PaddleYOLO 时期的理论课件（含原始图片） | 记录课程演进；其外部工程、示例路径与依赖在当前课程中已不存在 |
| `lessons/04-yolo-practice.md` | 旧 PaddleYOLO 时期的实践课件（含原始图片） | 同上；当前实践请读 `../lessons/04-yolo-practice.md` |

原中文 YOLO11 / PaddleYOLO Notebook 已按用户要求放回 `../notebooks/01-yolo11-rock-paper-scissors.ipynb`，作为课程原件对照。它依赖仓库外的 PaddleYOLO 工程（`yolo11_*_600e_coco.yml` 等配置、Linux 路径与旧数据包），在当前锁定环境中无法运行，因此只读、从不执行、不参与中英配对；这一处理登记在 `scripts/check_parity.py` 的 `HISTORY_IN_NOTEBOOKS` / `ONE_SIDED`，并由 `english/scripts/execute_and_save.py`、`english/scripts/verify_saved_outputs.py` 排除。查看它的历史改动：`git log --follow 02-object-detection/notebooks/01-yolo11-rock-paper-scissors.ipynb`（含它在 `archive/legacy-notebooks/` 期间的记录）。

英文课程在 `english/02-object-detection/archive/` 保留了另一件历史产物：旧数据包上跑出的 `01-yolo26-rps-legacy-executed.ipynb`，两边的历史材料不同，因此互为单侧内容，原因记录在 `english/02-object-detection/archive/README.md` 与 `scripts/check_parity.py` 的 `ONE_SIDED` 表中。
