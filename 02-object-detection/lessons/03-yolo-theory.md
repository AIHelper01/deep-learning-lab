# YOLO26 目标检测基础

本课程使用 Ultralytics YOLO26n。检测模型输出目标的位置、类别和置信度，与整张图一个标签的分类任务不同。

## 学习重点

- 输入为图像，监督信息为多个目标框与类别；YOLO 标注采用 `class_id xc yc w h`，几何量归一化到图片宽高。
- 特征提取网络与多尺度特征融合支持不同大小目标；检测头学习位置和类别，具体结构以当前 [YOLO26 官方说明](https://docs.ultralytics.com/models/yolo26/)为准。
- YOLO26 支持端到端推理路径，不应把其他 YOLO 版本的后处理细节无条件套用。课程使用 API 实际返回的框与分数。
- IoU 衡量预测框与真实框的交并比；precision/recall 分别反映误检与漏检；mAP50 与 mAP50-95 的 IoU 条件不同，数值不能直接互换。
- 用训练集学习参数、验证集选择设置、独立测试集最终评估。预训练 COCO 类别不等于石头剪刀布类别，需要微调。

## 本实验约定

采用 [Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1) 的原始 3,939/338/186 划分，模型 `yolo26n.pt`，原编号 `0=paper、1=rock、2=scissors`。`n` 表示此处选择的 nano 模型规模。框架、数据版本和随机种子都应随结果记录。

[继续实践](04-yolo-practice.md)；本模块第二个案例[车流量统计 Notebook](../notebooks/02-yolo26-vehicle-counting.ipynb) 在同一套检测输出上加入计数与过线判定。[格式转换与查看器专题](../dataset-formats/README.md)单独讨论文件格式与坐标约定，不在本节重新实现数据处理。

旧讲义保存在 [archive/lessons/](../archive/lessons/03-yolo-theory.md)，其中历史架构内容不代表本次实跑模型。
