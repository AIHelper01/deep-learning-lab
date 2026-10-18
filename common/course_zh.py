"""中文课程公共工具：为 matplotlib 选择可用的中文字体。

放在仓库根目录的 common/ 下（english/ 目录要求全英文，不允许出现中文字符），
中文课程的 BOOT 单元会把本目录加入 sys.path。
"""
from pathlib import Path

# macOS / Linux / Windows 上常见的中文字体名，按优先级排列。
CANDIDATES = [
    "PingFang SC",
    "Heiti SC",
    "Hiragino Sans GB",
    "Songti SC",
    "STHeiti",
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "Noto Sans SC",
    "Source Han Sans SC",
    "WenQuanYi Zen Hei",
    "Arial Unicode MS",
]


def chinese_font():
    """返回第一个系统里真实存在的中文字体名，找不到返回 None。"""
    from matplotlib import font_manager

    available = {font.name for font in font_manager.fontManager.ttflist}
    for name in CANDIDATES:
        if name in available:
            return name
    for name in sorted(available):
        if any(token in name for token in ("CJK", "Hei", "Song", "PingFang", "YaHei", "SC")):
            return name
    return None


def setup_chinese_fonts(plt_module=None):
    """设置中文图表字体，返回选中的字体名（便于在 notebook 中打印确认）。"""
    name = chinese_font()
    if name:
        import matplotlib

        matplotlib.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
        matplotlib.rcParams["axes.unicode_minus"] = False
    if plt_module is not None:
        plt_module.rcParams["axes.unicode_minus"] = False
    return name


def course_root_marker() -> Path:
    """中文课程根目录标记文件名。"""
    return Path("CHINESE_COURSE_ROOT")
