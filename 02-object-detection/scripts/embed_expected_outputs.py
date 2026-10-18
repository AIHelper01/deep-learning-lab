"""把已执行 Notebook 的输出改写成「预期输出」markdown 单元，写回 Notebook 本体。

用途：Notebook 被 Clear All Outputs（或首次打开）之后，读者仍能对照真实结果。
文字输出逐字摘录为 ```text 代码块；图片输出导出到平行 assets 目录并在 markdown 中
以相对路径引用，因此不依赖 Notebook 内嵌的 PNG。

本脚本现在只是仓库根目录通用脚本 `scripts/embed_expected_outputs.py` 的入口：
检测模块的图片前缀、手写图注与前言统一登记在通用脚本的 `OVERRIDES` 表里，
避免出现两份不同的内嵌逻辑。

用法（检测解释器或 ~/env_dl_uv 均可，任意目录执行）：

    ~/env_dl_uv/.venv/bin/python 02-object-detection/scripts/embed_expected_outputs.py

脚本可重复执行：带 course-expected-output 标签的单元会先删除再重新生成。
english/ 目录禁止出现中日韩文字，因此英文 Notebook 使用英文标签与说明。
"""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.argv = [str(ROOT / "scripts/embed_expected_outputs.py"), "--module", "02-object-detection"]
runpy.run_path(sys.argv[0], run_name="__main__")
