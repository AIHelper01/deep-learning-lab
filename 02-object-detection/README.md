# 目标检测

本模块为课程讲义和操作教程；训练、推理命令需要在外部 PaddleYOLO/PaddleDetection 工程中执行。

1. [CV 总览](lessons/01-cv-overview.md)
2. [CNN 基础](lessons/02-cnn-basics.md)
3. [YOLO 理论](lessons/03-yolo-theory.md)
4. [YOLO 实践](lessons/04-yolo-practice.md)
5. [剪刀石头布检测](notebooks/01-yolo11-rock-paper-scissors.ipynb)

## 运行前准备

- 准备与教程命令相符的 PaddleYOLO/PaddleDetection 工程，并记录实际版本或提交号；本项目未验证具体版本。
- 在外部工程准备剪刀石头布数据、VOC/COCO 标注、类别列表、训练配置和权重。
- 教程中的 tools/train.py、tools/infer.py、configs/、deploy/ 等相对于外部工程。
- /workspace、/home/aistudio 等路径及 Linux shell 命令是原环境示例。

讲义图片位于 assets/。原教程链接中的五个 yolo11 配置文件及 ONNX 导出文档未随项目提供，仍保留外部引用；见[整理记录](../docs/migration/reorganization.md)。不创建空配置冒充可运行配置。
