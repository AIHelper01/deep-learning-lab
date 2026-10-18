# 目标检测数据集格式专题：YOLO、VOC、COCO

[English](../../english/02-object-detection/dataset-formats/README.md) · 中文 · [项目首页](../../README.zh-CN.md)

本专题与模型训练平行：用同一份石头剪刀布数据解释标注格式、执行转换并查看结果。训练 Notebook 直接使用正式 YOLO 数据，不把格式转换混入训练流程。

## 1. 示例数据与来源

以 [Roboflow 数据集版本页](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset) 中的 [melikeavan / Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1) 为例，许可为 CC BY 4.0。用户提供的新包为 `Rock-Paper-Scissors.v1i.yolo26.zip`，包内元数据与该项目 v1 一致；训练 3,939 张、验证 338 张、测试 186 张。导出预处理为自动纠正方向、拉伸到 640×640，未做导出数据增强。

查看带框样本后确认原编号：**0=paper（布）、1=rock（石头）、2=scissors（剪刀）**。只将数字类别名称对应为英文语义，不重排标注编号。保留包内 README 与署名。早先 6,455 张图片的扁平 VOC 包不作为当前课程数据。

在仓库根目录准备检测环境后执行（只需导入一次，已存在目标目录时脚本拒绝覆盖）：

```powershell
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\fetch_rps.py --archive C:/Users/will/Downloads/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```

macOS/Linux 用课堂统一解释器，压缩包先按[数据说明](../data/README.md)放进 DataSet 暂存区：

```bash
~/env_dl_uv/.venv/bin/python english/scripts/fetch_rps.py \
  --archive /workspace/DataSet/yolo/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```

准备后的数据在 `english/02-object-detection/data/rock-paper-scissors-ishcs-v1/`，来源、版本、压缩包 SHA-256、类别顺序和真实计数保存在 `provenance.json`。中英文训练共用只读数据，输出分别存放。

## 2. 三种格式如何表达同一个框

假设图片为 640×640，目标框左上角 `(160,128)`、右下角 `(480,512)`：

| 格式 | 保存内容 | 示例 |
|---|---|---|
| YOLO TXT | 从 0 开始的类别编号、归一化中心点及宽高 | `0 0.5 0.5 0.5 0.6` |
| VOC XML | 类别名称、像素角点 xmin/ymin/xmax/ymax | `paper`，`160,128,480,512`（按本专题连续坐标约定） |
| COCO JSON | 图片 ID、类别 ID、左上角像素位置与宽高 | `category_id=1`，`bbox=[160,128,320,384]`，`area=122880` |

```text
YOLO → 角点（W/H 为图片宽高）
xmin = (xc - w/2) × W       xmax = (xc + w/2) × W
ymin = (yc - h/2) × H       ymax = (yc + h/2) × H
角点 → COCO：[xmin, ymin, xmax-xmin, ymax-ymin]
角点 → YOLO：[(xmin+xmax)/(2W), (ymin+ymax)/(2H), (xmax-xmin)/W, (ymax-ymin)/H]
```

COCO 类别 ID 不保证从 0 开始或连续，本脚本导出为 1/2/3，通过 `categories` 名称和 `classes.json` 显式映射；YOLO 保留 0/1/2，不直接照搬数字。

传统 VOC 工具常用从 1 开始、边界包含端点的整数坐标。本专题为往返精度显式采用 `zero-based-continuous-xyxy`，写入 XML 的 `coordinate_convention` 字段并保留浮点坐标；读取器只接受这个声明。任意历史 VOC 数据应先明确坐标约定，再做适配，不能机械加减 1 或取整，否则框会发生偏移。这也意味着本脚本不是任意 VOC 文件的通用导入器。

## 3. 实际转换命令

脚本位置是 [english/scripts/dataset_formats.py](../../english/scripts/dataset_formats.py)，使用检测环境中已有的 Pillow 和 PyYAML。所有命令从仓库根目录运行。先选独立测试集的 186 张图片做教学验证，不改变训练数据：

```powershell
$py = '.\english\02-object-detection\.venv\Scripts\python.exe'
$source = '.\english\02-object-detection\data\rock-paper-scissors-ishcs-v1'
& $py .\english\scripts\dataset_formats.py --source $source --input-format yolo --output-format voc --split test --destination .\english\02-object-detection\dataset-formats\data\rps-voc-test
& $py .\english\scripts\dataset_formats.py --source $source --input-format yolo --output-format coco --split test --destination .\english\02-object-detection\dataset-formats\data\rps-coco-test
& $py .\english\scripts\dataset_formats.py --source .\english\02-object-detection\dataset-formats\data\rps-voc-test --input-format voc --output-format yolo --split test --destination .\english\02-object-detection\dataset-formats\data\rps-yolo-from-voc
& $py .\english\scripts\dataset_formats.py --source .\english\02-object-detection\dataset-formats\data\rps-coco-test --input-format coco --output-format yolo --split test --destination .\english\02-object-detection\dataset-formats\data\rps-yolo-from-coco
```

```bash
py=~/env_dl_uv/.venv/bin/python
source=english/02-object-detection/data/rock-paper-scissors-ishcs-v1
$py english/scripts/dataset_formats.py --source $source --input-format yolo --output-format voc --split test --destination english/02-object-detection/dataset-formats/data/rps-voc-test
$py english/scripts/dataset_formats.py --source $source --input-format yolo --output-format coco --split test --destination english/02-object-detection/dataset-formats/data/rps-coco-test
$py english/scripts/dataset_formats.py --source english/02-object-detection/dataset-formats/data/rps-voc-test --input-format voc --output-format yolo --split test --destination english/02-object-detection/dataset-formats/data/rps-yolo-from-voc
$py english/scripts/dataset_formats.py --source english/02-object-detection/dataset-formats/data/rps-coco-test --input-format coco --output-format yolo --split test --destination english/02-object-detection/dataset-formats/data/rps-yolo-from-coco
```

改用 `--split all` 可转换现有 train/valid/test 三个划分；VOC→COCO、COCO→VOC 只需对应设置 `--input-format` 与 `--output-format`。输入需要符合本专题约定的目录，VOC/COCO 需要 `classes.json`，外部数据布局先行适配。

```text
YOLO                          VOC                          COCO
  data.yaml                     classes.json                 classes.json
  classes.txt                   classes.txt                  classes.txt
  test/images/*.jpg             test/JPEGImages/*.jpg        test/images/*.jpg
  test/labels/*.txt              test/Annotations/*.xml       annotations/instances_test.json
```

每份结果包含 `conversion.json`，记录类别顺序、图片数、框数。转换不改变图片字节、空标注图片、原始划分与支持的目标框，不自动重划分、裁框、缩放或增强。遇到目标目录已存在、缺少标签、未知类别、越界框、分割/人群标注或未声明的 VOC 坐标约定会报错。这里只处理轴对齐检测框，不承诺保留分割、关键点、旋转框、difficult/crowd 等额外语义。

## 4. 使用小土堆 Labs 查看数据集

打开[小土堆实验室](https://xiaotudui.com/labs)，选择相应查看器。2026-10-18 已逐一核对三个页面的界面；以下是可按图执行的说明，本次界面核对不等于已经把数据导入网站。

| 查看器 | 图片文件 | 标注文件 |
|---|---|---|
| [YOLO 查看器](https://xiaotudui.com/labs/yolo-dataset-viewer) | `test/images/` 中图片 | `test/labels/` 下同名 TXT |
| [VOC 查看器](https://xiaotudui.com/labs/voc-dataset-viewer) | `test/JPEGImages/` 中图片 | `test/Annotations/` 下同名 XML |
| [COCO 查看器](https://xiaotudui.com/labs/coco-dataset-viewer) | `test/images/` 中图片 | 含该图片记录的 `annotations/instances_test.json` |

1. 点击对应格式查看器，选择本专题的公开石头剪刀布示例图片。
2. 点击“上传图片文件”，再选择“上传YOLO标注文件”“上传VOC标注文件”或“上传COCO标注文件”。图片和标注必须对应同一张图。
3. 点击“开始标注”查看边界框，用缩放滑块或“重置视图”调整。COCO 页面另有“搜索ID”，对应 JSON 中的图片 ID，不是标注 ID。
4. YOLO 页面说明要求 `classes.txt`（每行一个名称）；实际观察到的界面只有图片与标注选择入口，没有独立类别文件按钮。保留 `classes.txt`，如界面只显示编号就按类别顺序核对；不要假定网页自动读取 `data.yaml`。
5. 用同一张图对比三种格式：框数、角点位置、类别语义、是否与图片对齐应一致。空标注图片应仍为空。出现偏移或细线框，先检查宽高、坐标归一化、VOC 原点及端点约定、类别 ID 映射。

## 5. 转换完成标准

使用检测解释器运行 [english/scripts/check_dataset_formats.py](../../english/scripts/check_dataset_formats.py)，检查三种格式的六个转换方向和异常处理，并对真实测试集做往返比对。对比图片哈希、划分、类别、目标框数量、像素坐标（允许序列化小数误差）。执行真实数据验证后，结果写入 `english/reports/dataset-formats-validation.json`；格式转换不会生成模型准确率。

参考：[Ultralytics YOLO 检测格式](https://docs.ultralytics.com/datasets/detect/)、[COCO 格式](https://cocodataset.org/#format-data)、[Pascal VOC](http://host.robots.ox.ac.uk/pascal/VOC/)，以及上面的三个查看器页面。

```powershell
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\check_dataset_formats.py
.\english\02-object-detection\.venv\Scripts\python.exe .\english\scripts\check_dataset_formats.py --source .\english\02-object-detection\data\rock-paper-scissors-ishcs-v1
```

```bash
~/env_dl_uv/.venv/bin/python english/scripts/check_dataset_formats.py
~/env_dl_uv/.venv/bin/python english/scripts/check_dataset_formats.py --source english/02-object-detection/data/rock-paper-scissors-ishcs-v1
```

第二条命令生成上面的示例目录；目录已存在时拒绝覆盖。重复验证可指定新的空 `--output-root`，不要删除或覆盖原始数据。
