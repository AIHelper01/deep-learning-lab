# 迁移说明

来源：E:/ai-showcase；目标：E:/deep-learning-lab。

迁入原文件 61 个，其中图片 29 个；排除 26 个文件；修复图片路径 15 处。

跨模块检查：未发现需要从这三个目录之外补入的现存本地文件。网络资源维持原链接。

## 原有外部依赖与缺失文件

以下链接在原仓库中即无对应文件，保留原文，需在教程要求的外部 PaddleDetection/PaddleYOLO 工程内使用：

- `2.2深度学习-ObjectDetection\基于YOLOv11完成剪刀石头布目标检测.ipynb` → `./yolo11_n_600e_coco.yml`
- `2.2深度学习-ObjectDetection\基于YOLOv11完成剪刀石头布目标检测.ipynb` → `./yolo11_s_600e_coco.yml`
- `2.2深度学习-ObjectDetection\基于YOLOv11完成剪刀石头布目标检测.ipynb` → `./yolo11_m_600e_coco.yml`
- `2.2深度学习-ObjectDetection\基于YOLOv11完成剪刀石头布目标检测.ipynb` → `./yolo11_l_600e_coco.yml`
- `2.2深度学习-ObjectDetection\基于YOLOv11完成剪刀石头布目标检测.ipynb` → `./yolo11_x_600e_coco.yml`
- `2.2深度学习-ObjectDetection\基于YOLOv11完成剪刀石头布目标检测.ipynb` → `../../deploy/EXPORT_ONNX_MODEL.md`

LEDNUM 数据及其 train.txt/test.txt、AI Studio insects 数据、PaddleYOLO 剪刀石头布数据/训练权重需按课程准备，原仓库未附带。YOLO实践中 /home/aistudio 等路径属于原教程环境示例。Notebook 历史输出保留，输出中的旧路径属于运行记录。

## 路径修复

- `2.2深度学习-ObjectDetection\CV基础_PPT内容梳理版.md`：`output_11_1.png` → `image/output_11_1.png`
- `2.2深度学习-ObjectDetection\CV基础_PPT内容梳理版.md`：`output_14_0.png` → `image/output_14_0.png`
- `2.2深度学习-ObjectDetection\CV基础_PPT内容梳理版.md`：`output_16_0.png` → `image/output_16_0.png`
- `2.2深度学习-ObjectDetection\CV基础_PPT内容梳理版.md`：`output_12_0.png` → `image/output_12_0.png`
- `2.2深度学习-ObjectDetection\CV基础_PPT内容梳理版.md`：`output_15_1.png` → `image/output_15_1.png`
- `2.2深度学习-ObjectDetection\YOLO实践`：`E:/ai-showcase/2.2深度学习-ObjectDetection/image/output_19_1.png` → `image/output_19_1.png`
- `2.2深度学习-ObjectDetection\YOLO实践`：`E:/ai-showcase/2.2深度学习-ObjectDetection/image/output_21_0.png` → `image/output_21_0.png`
- `2.2深度学习-ObjectDetection\YOLO实践`：`E:/ai-showcase/2.2深度学习-ObjectDetection/image/output_23_1.png` → `image/output_23_1.png`
- `2.2深度学习-ObjectDetection\YOLO实践`：`E:/ai-showcase/2.2深度学习-ObjectDetection/image/output_25_0.png` → `image/output_25_0.png`
- `2.2深度学习-ObjectDetection\YOLO实践`：`E:/ai-showcase/2.2深度学习-ObjectDetection/image/output_29_1.png` → `image/output_29_1.png`
- `2.2深度学习-ObjectDetection\YOLO实践`：`E:/ai-showcase/2.2深度学习-ObjectDetection/image/output_60_0.png` → `image/output_60_0.png`
- `2.2深度学习-ObjectDetection\YOLO理论`：`E:\ai-showcase\2.2深度学习-ObjectDetection\image\arXiv-2509.25164-v2.0-figure-1.png` → `image/arXiv-2509.25164-v2.0-figure-1.png`
- `2.2深度学习-ObjectDetection\YOLO理论`：`E:\ai-showcase\2.2深度学习-ObjectDetection\image\arXiv-2509.25164-v2.0-figure-2.png` → `image/arXiv-2509.25164-v2.0-figure-2.png`
- `2.2深度学习-ObjectDetection\YOLO理论`：`E:\ai-showcase\2.2深度学习-ObjectDetection\image\arXiv-2509.25164-v2.0-figure-3.png` → `image/arXiv-2509.25164-v2.0-figure-3.png`
- `2.2深度学习-ObjectDetection\YOLO理论`：`E:\ai-showcase\2.2深度学习-ObjectDetection\image\arXiv-2509.25164-v2.0-figure-4.png` → `image/arXiv-2509.25164-v2.0-figure-4.png`

## 未迁入的文件

- `2.1深度学习-ImageClassification\LeNet-5\DataSet\MNIST\raw\t10k-images-idx3-ubyte.gz`：已有内容相同的解压数据文件
- `2.1深度学习-ImageClassification\LeNet-5\DataSet\MNIST\raw\t10k-labels-idx1-ubyte.gz`：已有内容相同的解压数据文件
- `2.1深度学习-ImageClassification\LeNet-5\DataSet\MNIST\raw\train-images-idx3-ubyte.gz`：已有内容相同的解压数据文件
- `2.1深度学习-ImageClassification\LeNet-5\DataSet\MNIST\raw\train-labels-idx1-ubyte.gz`：已有内容相同的解压数据文件
- `2.1深度学习-ImageClassification\main.py`：仅输出 Hello from 的占位脚本
- `2.1深度学习-ImageClassification\ResNet\images\index-Copy1.png`：未被课程文档或代码引用的图片
- `2.1深度学习-ImageClassification\ResNet\images\index.png`：未被课程文档或代码引用的图片
- `2.1深度学习-ImageClassification\ResNet\images\lednum.png`：未被课程文档或代码引用的图片
- `2.1深度学习-ImageClassification\ResNet\images\mnist.jpg`：未被课程文档或代码引用的图片
- `2.1深度学习-ImageClassification\ResNet\images\padding.png`：未被课程文档或代码引用的图片
- `2.1深度学习-ImageClassification\ResNet\images\path.png`：未被课程文档或代码引用的图片
- `2.1深度学习-ImageClassification\ResNet\images\test_cat.jpg`：未被课程文档或代码引用的图片
- `2.1深度学习-ImageClassification\ResNet\images\test_dog.jpg`：未被课程文档或代码引用的图片
- `2.1深度学习-ImageClassification\ResNet\images\test_led.jpg`：未被课程文档或代码引用的图片
- `2.1深度学习-ImageClassification\ResNet\images\test_mnist.jpg`：未被课程文档或代码引用的图片
- `2.3深度学习-SentimentAnalysis\main.py`：仅输出 Hello from 的占位脚本

- `2.1深度学习-ImageClassification\LeNet-5\images\padding.png`：未被课程文档或代码引用的图片

- `2.2深度学习-ObjectDetection\image\29755414bb1347bb834bd7835faa1320d91f98cefcd1468e85f8409238994879.png`：未被课程文档或代码引用的图片

- `2.2深度学习-ObjectDetection\image\368c6656e0364563b5d26e0f81b94755dba944a271c14b18bc112c3d6ea6d106.jfif`：未被课程文档或代码引用的图片

- `2.2深度学习-ObjectDetection\image\70d8475ed908487680057bf1f2760f10e367e7176acf43ebb380207b748b2377.png`：未被课程文档或代码引用的图片

- `2.2深度学习-ObjectDetection\image\8ba9786060524ccc9a71d1ba1f905f85701282afd36d4df9a46395ec197138e2.png`：未被课程文档或代码引用的图片

- `2.2深度学习-ObjectDetection\image\90513f72043a4ec3bb74560c1014822292211a27c39641f9b9b732b83cdb09bd.png`：未被课程文档或代码引用的图片

- `2.2深度学习-ObjectDetection\image\93476b373dd342d1aae22397aa24c58fc60ab68307fd448189f16c8284723e9d.png`：未被课程文档或代码引用的图片

- `2.2深度学习-ObjectDetection\image\93476b373dd342d1aae22397aa24c58fc60ab68307fd448189f16c8284723e9d2.png`：未被课程文档或代码引用的图片

- `2.2深度学习-ObjectDetection\image\d1468aff55cf4e68a504cd876b1e017c4d1cd2f9dc90494eaaff4c80ec03c32e.jfif`：未被课程文档或代码引用的图片

- `2.2深度学习-ObjectDetection\image\image-20260908224619680.png`：未被课程文档或代码引用的图片

## 校验

对所有复制文件逐一校验 SHA-256（明确修改的文档除外）；检查现存本地引用的目标均已复制，检查 Notebook JSON 可解析且代码单元、输出保持不变。未执行模型训练，未验证远程资源可访问性。
