# 检测数据

本模块的所有数据集都经过校验导入器进入 `data/`，而不是直接复制：导入器会在数据旁写入 `provenance.json`，记录来源元数据、压缩包 SHA-256、类别名与实测数量。下面每个数据集都给出 **cp 方式**（把已有的压缩包放进 DataSet 暂存区再导入）和**下载方式**（压缩包从哪里获取）。数据不提交 Git；目标目录已存在时导入器拒绝覆盖，因此每份数据只导入一次。

[数据集目录](../../docs/datasets.zh-CN.md#石头剪刀布yolo26-目标检测) · [车辆计数说明](../../docs/datasets.zh-CN.md#车辆计数车流量统计yolo26) · [VOC / COCO / YOLO 转换与小土堆查看器](../dataset-formats/README.md) 是独立专题，不混入训练流程。

## 石头剪刀布 v1

来源：[melikeavan / Rock-Paper-Scissors v1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1)，CC BY 4.0。中英文 YOLO26n 课程共用 `english/02-object-detection/data/rock-paper-scissors-ishcs-v1/`，两侧各自写入本模块 `outputs/`。

正式 YOLO26 导出为训练 3,939 / 验证 338 / 测试 186 张，标注框 4,610 / 400 / 204 个。已逐图核对类别顺序：**0=paper、1=rock、2=scissors**，只补充英文名称，编号、标注和划分不变。历史镜像包与扁平 VOC 包不用于默认训练。

### 从 DataSet 拉取（cp 方式）

```bash
# 在仓库根目录执行；暂存区按“一个数据集一个压缩包”保存
mkdir -p /workspace/DataSet/yolo
cp "/path/to/Rock-Paper-Scissors.v1i.yolo26.zip" /workspace/DataSet/yolo/
uv run python english/scripts/fetch_rps.py \
  --archive /workspace/DataSet/yolo/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```

Windows PowerShell（先在仓库根 `uv sync`）：

```powershell
uv run python .\english\scripts\fetch_rps.py --archive C:/Users/will/Downloads/Rock-Paper-Scissors.v1i.yolo26.zip --class-names paper rock scissors
```

已解压的正式导出可放在任意目录，再用 `--export-dir <目录>` 导入。直接 `cp -R <已解压导出> english/02-object-detection/data/rock-paper-scissors-ishcs-v1/` 也能跑通，但会缺少导入器写出的 `provenance.json`，因此推荐走导入器。

### 下载方式

**浏览器方式**：打开 [dataset 1](https://universe.roboflow.com/melikeavan/rock-paper-scissors-ishcs/dataset/1) → *Download Dataset* → 格式选 **YOLO26** → *Download for computer vision*，把压缩包保存为 `/workspace/DataSet/yolo/Rock-Paper-Scissors.v1i.yolo26.zip` 后按上面的 cp 方式导入。

**API key 方式**：导出归属于账号，所以网页按钮需要登录，但导出 REST 接口接受个人 API key，用 `curl` 就能直接拿到同一个 ZIP。key 在 Roboflow 账号设置页复制，请存放在仓库之外，切勿提交到 Git：

```bash
umask 077 && printf '%s' 'YOUR_ROBOFLOW_API_KEY' > ~/.config/roboflow_api_key && chmod 600 ~/.config/roboflow_api_key

LINK=$(curl -sS -G "https://api.roboflow.com/melikeavan/rock-paper-scissors-ishcs/1/yolo26" \
  --data-urlencode "api_key=$(cat ~/.config/roboflow_api_key)" \
  --data-urlencode "nocache=true" \
  | python -c 'import json,sys; print(json.load(sys.stdin)["export"]["link"])')
curl -sSL "$LINK" -o "/workspace/DataSet/yolo/Rock-Paper-Scissors.v1i.yolo26.zip"
```

接口返回里的 `progress` 是 0~1 的导出进度，`export.size` 单位 MB；请重复第一个请求直到 `progress` 为 `1` 再跟随链接下载。`roboflow` SDK 的 `project.version(1).export("yolo26")` 走的是同一个接口。

## 车辆计数 v4（车流量统计案例）

来源：[vehicle-counting-rtvul / vehicle-counting-tksu5 v4](https://universe.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/dataset/4)，CC BY 4.0。中英文共用 `english/02-object-detection/data/vehicle-counting-tksu5-v4/`，各自运行自己的 Notebook：英文 `english/02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb`、中文 `02-object-detection/notebooks/02-yolo26-vehicle-counting.ipynb`，输出分别写入两侧 `outputs/`。

正式 YOLO26 导出共 6,565 张、5 类，保留原划分：训练 4,708 / 验证 1,661 / 测试 196 张，标注框 52,668 / 18,810 / 2,120 个。类别编号保持原顺序、名称统一小写：**0=truck、1=bicycle、2=bus、3=car、4=motorcycle**（原包 `Truck` 首字母大写）。源包有 3 行标注是分割多边形，导入时改写为其外接检测框并记入 `provenance.json`。

### 从 DataSet 拉取（cp 方式）

```bash
# 在仓库根目录执行
mkdir -p /workspace/DataSet/yolo
cp "/path/to/vehicle counting.v4i.yolo26.zip" /workspace/DataSet/yolo/
uv run python english/scripts/import_vehicle_counting.py --from-staging
# 或者显式指定某个压缩包
uv run python english/scripts/import_vehicle_counting.py --archive "/workspace/DataSet/yolo/vehicle counting.v4i.yolo26.zip"
```

暂存区不在默认位置时加 `--staging <目录>`。Windows PowerShell 等价命令（先在仓库根 `uv sync`）：

```powershell
uv run python .\english\scripts\import_vehicle_counting.py --from-staging
```

导入器核对 Roboflow 元数据、类别、数量与压缩包 SHA-256 后写入 `data/vehicle-counting-tksu5-v4/` 与 `provenance.json`。

### 下载方式

**浏览器方式**：打开 [dataset 4](https://universe.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/dataset/4) → *Download Dataset* → 格式选 **YOLO26** → *Download for computer vision*，把 ZIP 保存为 `/workspace/DataSet/yolo/vehicle counting.v4i.yolo26.zip`。元数据与 dataset 4 不一致的压缩包会被导入器拒绝。

**API key 方式**：导出 REST 接口接受个人 API key，不需要浏览器会话。key 的存放方式见上面「石头剪刀布」一节，务必放在仓库之外：

```bash
LINK=$(curl -sS -G "https://api.roboflow.com/vehicle-counting-rtvul/vehicle-counting-tksu5/4/yolo26" \
  --data-urlencode "api_key=$(cat ~/.config/roboflow_api_key)" \
  --data-urlencode "nocache=true" \
  | python -c 'import json,sys; print(json.load(sys.stdin)["export"]["link"])')
curl -sSL "$LINK" -o "/workspace/DataSet/yolo/vehicle counting.v4i.yolo26.zip"
```

先重复第一个请求直到 `progress` 为 `1` 再跟随链接；导出完成后 `export.size` 应为 525.0 MB。

## COCO8（仅流程检查）

`COURSE_SMOKE=1` 使用 Ultralytics 的 [COCO8](https://docs.ultralytics.com/datasets/detect/coco8/) 样例，几秒内即可验证流程。Ultralytics 首次使用时自动下载到本模块数据目录，无需暂存；它的分数不能作为课程实验结果。
