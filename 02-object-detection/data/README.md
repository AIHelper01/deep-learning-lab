# 石头剪刀布 v1 数据（中文 YOLO26）

来源：[melikeavan / Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1)，CC BY 4.0。中英文采用同一份正式 YOLO26 导出及锁定环境，原划分为训练 3,939 张、验证 338 张、测试 186 张。

数据统一存于 `english/02-object-detection/data/rock-paper-scissors-ishcs-v1/`（仓库根目录相对路径）；中文训练产物写入本模块 `outputs/`。已查看标注确认 **0=paper、1=rock、2=scissors**，仅赋英文名称，不改变编号、标注和划分。来源、压缩包哈希及真实计数见数据目录的 `provenance.json`。

导入命令与条款见[中文数据集指南](../../docs/datasets.zh-CN.md)。历史 PaddleYOLO 教程保留为对照，旧镜像与早先扁平 VOC 包不用于默认训练。

[VOC / COCO / YOLO 转换及小土堆查看器说明](../../04-dataset-formats/README.zh-CN.md)作为独立专题维护，不混入训练流程。数据不提交 Git。
