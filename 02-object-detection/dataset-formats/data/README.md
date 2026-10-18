# 转换输出目录（自动生成，不提交）

这里只保存 `english/scripts/dataset_formats.py` 生成的结果：`rps-voc-test/`、`rps-coco-test/`、
`rps-yolo-from-voc/`、`rps-yolo-from-coco/`。它们是可随时重跑的练习产物，因此不提交 Git。
专题说明：[中文](../README.md) · [English](../../../english/02-object-detection/dataset-formats/README.md)。

## 输入数据不放在这里

转换脚本与一致性检查读取的都是检测模块里的 YOLO 数据：
`english/02-object-detection/data/rock-paper-scissors-ishcs-v1/`。在仓库根目录导入一次即可。

**cp 方式** —— 把已有压缩包拷进 DataSet 暂存区，再执行导入器：

```bash
mkdir -p /workspace/DataSet/yolo
cp "/path/to/Rock-Paper-Scissors.v1i.yolo26.zip" /workspace/DataSet/yolo/
~/env_dl_uv/.venv/bin/python english/scripts/fetch_rps.py \
  --archive /workspace/DataSet/yolo/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```

**下载方式** —— Roboflow 需要登录，`curl` 无法直接下载。打开
[Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1) →
*Download Dataset* → 格式选 **YOLO26**，把 ZIP 保存到 `/workspace/DataSet/yolo/`，再按上面的 cp 方式导入。

来源、数量、类别编号与 `--export-dir` 的替代路径见检测模块的数据说明：
[English](../../../english/02-object-detection/data/README.md) · [中文](../../data/README.md)。
