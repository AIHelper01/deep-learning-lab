# YOLO26 实践：石头剪刀布

在仓库根目录按[模块说明](../README.md)准备检测环境和正式 v1 数据，打开 [YOLO26 Notebook](../notebooks/01-yolo26-rock-paper-scissors.ipynb)。当前实践采用 Ultralytics，与历史外部 PaddleYOLO 工程流程独立。

## 实验步骤

1. 核对数据源为 melikeavan / rock-paper-scissors-ishcs v1，原始划分为训练 3,939、验证 338、测试 186。核对类别顺序与数据目录的 `provenance.json`。
2. 执行路径与环境单元，使用与英文版相同的检测环境。数据共用只读导出，中文产物写到本模块 outputs。
3. 执行数据校验。缺失标注、错误来源、非法坐标和跨集合完全重复图片会报错；不要关闭校验绕过数据问题。
4. 加载 `yolo26n.pt`，使用训练单元中的 epochs/imgsz/batch 设置。CPU 默认 320 像素、10 轮；实际快速运行设置 `COURSE_EPOCHS=1`，仍使用全部训练数据。
5. 检查真实训练曲线和 best checkpoint。用独立 test 划分计算 mAP50/mAP50-95，并查看混淆矩阵和带框预测。
6. 记录失败样本、置信度阈值、设备、耗时和框架版本；不同轮数或数据来源的指标分开报告。

`COURSE_SMOKE=1` 改用 COCO8，不能用来证明手势识别准确率。预训练权重首次下载需要联网。Windows Notebook 使用 workers=0 避免多进程问题。

VOC、COCO、YOLO 互转与[小土堆 Labs](https://xiaotudui.com/labs)说明在[独立专题](../../04-dataset-formats/README.zh-CN.md)，不是运行本实验的前置转换步骤。

历史叶病虫害实践保存在[归档讲义](../archive/lessons/04-yolo-practice.md)，其中旧路径、数据和模型与本实验不同。
