#!/usr/bin/env python3
"""审计全仓库（中英两侧）的文档链接、图片本地化与 assets 命名规范。

检查项：
1. 本地链接可达：markdown 的 `[..](路径)`、`![..](路径)` 与 HTML `<img src="路径">` 都解析；
2. 不允许远程图片：文档与 notebook 里的图片必须已经下载到本地 assets；
3. assets 命名规范：每个文件必须是 `<名称>-<序号>.<扩展名>`，assets 目录内不再嵌套子目录；
4. 双语配对：`docs/*.md` 必须有同名 `.zh-CN.md`，含 `README.zh-CN.md` 的目录必须有 `README.md`，且互相链接；
5. 链接锚点：`文档.md#小节` 指向的小节标题必须真的存在（按 GitHub 的 slug 规则比对）；
6. notebook 内的 markdown 同样参与检查 1、2 与 5。

用法（仓库根目录）：
    ~/env_dl_uv/.venv/bin/python scripts/check_docs_assets.py
"""
from pathlib import Path
import json
import unicodedata
import re

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "__pycache__", ".ipynb_checkpoints", "data", "outputs",
             "logs", "node_modules", ".pytest_cache", "original"}
MD_LINK = re.compile(r'\[[^\]]*\]\(([^)\s]+)')
MD_IMAGE = re.compile(r'!\[[^\]]*\]\(([^)\s]+)')
HTML_IMAGE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.I)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
ASSET_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*-\d+\.(?:png|jpg|jpeg|gif|svg|webp)$")
# 历史课件的输入图按迁移记录（docs/migration/file-map.json）放在 assets/<子目录>/<名称>.<ext> 下，
# 归档 notebook 的代码就是按那个相对路径读图的；改路径等于改历史课件，所以这一个目录豁免扁平命名规范，
# 里面也不是本次实跑产出的「预期输出」图片，不参与 `<名称>-<序号>` 检查。
HISTORICAL_ASSET_DIRS = {
    "01-image-classification/archive/assets/lenet":
        "restores ../assets/lenet/test_cifar10.png, the input image read by "
        "legacy-notebooks/02-lenet-cifar10.ipynb; the path follows docs/migration/file-map.json",
}

# docs/ 下的迁移记录只保留英文原文，不参与双语配对。
BILINGUAL_EXEMPT = {"docs/migration/reorganization.md", "docs/migration/original"}


def is_data_document(path):
    """数据目录只允许 README 这类说明文档进入检查，原始数据不参与。"""
    return "data" in path.parts


def markdown_cells(path):
    nb = json.loads(path.read_text(encoding="utf-8"))
    for index, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") == "markdown":
            yield f"cell {index}", "".join(cell.get("source", []))


def author_markdown():
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS or part.startswith(".venv") for part in rel.parts):
            # 数据目录里的说明文档（README.md / README.zh-CN.md）仍然参与链接检查，原始数据不参与
            if not (path.name.startswith("README") and path.parent.name == "data"):
                continue
        if not path.is_file():
            continue
        if path.suffix == ".md":
            yield path, [(Path(path).name, path.read_text(encoding="utf-8"))]
        elif path.suffix == ".ipynb":
            yield path, list(markdown_cells(path))


# 历史 notebook 允许引用外部 PaddleYOLO 工程里从未进入本仓库的文件；
# 但引用本课程自己的文件必须可达，因此只有“看起来属于外部工程”的链接记为说明项。
EXTERNAL_LEGACY = re.compile(r"\.(yml|yaml|md)$")
# 原中文 YOLO11 教程已按用户要求放回 notebooks/，仍按只读历史对待。
LEGACY_NOTEBOOK_NAMES = {"01-yolo11-rock-paper-scissors.ipynb"}


def is_external_legacy(path, link):
    return (("legacy-notebooks" in path.parts or path.name in LEGACY_NOTEBOOK_NAMES)
            and "assets/" not in link
            and bool(EXTERNAL_LEGACY.search(link)))


def check_links(problems, legacy_notes):
    remote_images = 0
    for path, chunks in author_markdown():
        for label, text in chunks:
            text = re.sub(r"```[\s\S]*?```", "", text)   # 代码块里的方括号不是链接
            for link in MD_LINK.findall(text):
                if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://|^#|^mailto:", link):
                    continue
                target = (path.parent / link.split("#")[0]).resolve()
                if link.split("#")[0] and not target.exists():
                    message = f"Broken link: {path.relative_to(ROOT)} {label}: {link}"
                    if is_external_legacy(path, link):
                        legacy_notes.append(message)   # 外部工程文件，归档只读，见其 README
                    else:
                        problems.append(message)
            for image in MD_IMAGE.findall(text) + HTML_IMAGE.findall(text):
                if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", image):
                    remote_images += 1
                    problems.append(f"Remote image: {path.relative_to(ROOT)} {label}: {image}")
    return remote_images


def check_assets(problems, historical_asset_dirs):
    for assets in sorted(ROOT.rglob("assets")):
        rel = assets.relative_to(ROOT)
        if any(part in SKIP_DIRS or part.startswith(".venv") for part in rel.parts):
            continue
        if not assets.is_dir():
            continue
        for entry in sorted(assets.iterdir()):
            if entry.is_dir():
                note = HISTORICAL_ASSET_DIRS.get((rel / entry.name).as_posix())
                if note:
                    historical_asset_dirs.append(f"{(rel / entry.name).as_posix()}: {note}")
                    continue
                problems.append(f"Nested directory in assets: {entry.relative_to(ROOT)}")
            elif entry.name == "README.md" or entry.suffix.lower() not in IMAGE_SUFFIXES:
                continue          # 说明文件与非图片数据（如词表 JSON）不受图片命名规范约束
            elif not ASSET_NAME.match(entry.name):
                problems.append(f"Asset name must be <name>-<N>.<ext>: {entry.relative_to(ROOT)}")


def check_bilingual(problems):
    docs = {p for p in (ROOT / "docs").rglob("*.md")
            if not any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts)}
    for path in sorted(docs):
        rel = path.relative_to(ROOT).as_posix()
        if rel in BILINGUAL_EXEMPT or "/original/" in rel:
            continue
        if path.name.endswith(".zh-CN.md"):
            english = path.with_name(path.name[:-len(".zh-CN.md")] + ".md")
            if not english.is_file():
                problems.append(f"Bilingual doc missing English half: {rel}")
            elif path.name not in english.read_text(encoding="utf-8"):
                problems.append(f"English doc does not link its Chinese half: {english.relative_to(ROOT)}")
        elif not (path.with_name(path.stem + ".zh-CN.md")).is_file():
            problems.append(f"Bilingual doc missing Chinese half: {rel}")
    for readme_zh in sorted(ROOT.rglob("README.zh-CN.md")):
        rel = readme_zh.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        english = readme_zh.with_name("README.md")
        if not english.is_file():
            problems.append(f"Bilingual README missing English half: {rel}")
        elif "README.zh-CN.md" not in english.read_text(encoding="utf-8"):
            problems.append(f"README does not link its Chinese half: {english.relative_to(ROOT)}")


def github_slug(heading_line):
    """按 GitHub 的规则把标题行变成锚点：小写、去标点、空格转连字符，保留字母数字与 CJK。"""
    text = heading_line.strip().lstrip("#").strip().lower()
    kept = [c for c in text
            if c.isalnum() or c in " -_" or unicodedata.category(c).startswith("L")]
    return "".join(kept).strip().replace(" ", "-")


def check_anchors(problems):
    """`[文字](某文档.md#小节)` 里的 `#小节` 必须是该文档里真实存在的标题。"""
    anchors = {}
    for path, _ in author_markdown():
        if path.suffix == ".md":
            anchors[path.resolve()] = {github_slug(line)
                                       for line in path.read_text(encoding="utf-8").splitlines()
                                       if line.startswith("#")}
    checked = 0
    for path, chunks in author_markdown():
        for label, text in chunks:
            text = re.sub(r"```[\s\S]*?```", "", text)   # 代码块里的方括号不是链接
            for link in MD_LINK.findall(text):
                if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://|^mailto:", link) or "#" not in link:
                    continue
                target, fragment = link.split("#", 1)
                if not fragment:
                    continue
                checked += 1
                resolved = (path.parent / target).resolve() if target else path.resolve()
                if resolved not in anchors:
                    problems.append(f"Anchor target is not an authored document: "
                                    f"{path.relative_to(ROOT)} {label}: {link}")
                elif fragment not in anchors[resolved]:
                    problems.append(f"Unknown anchor: {path.relative_to(ROOT)} {label}: {link}")
    return checked


def main():
    problems, legacy_notes, historical_asset_dirs = [], [], []
    remote_images = check_links(problems, legacy_notes)
    fragments = check_anchors(problems)
    check_assets(problems, historical_asset_dirs)
    check_bilingual(problems)
    report = {
        "markdown_documents": sum(1 for p, _ in author_markdown() if p.suffix == ".md"),
        "link_fragments_checked": fragments,
        "remote_images": remote_images,
        "legacy_external_links": len(legacy_notes),
        "legacy_external_link_examples": legacy_notes[:5],
        "historical_asset_dirs": historical_asset_dirs,
        "legacy_external_link_reason": "read-only history notebooks (archive/legacy-notebooks and the "
        "original YOLO11 lesson kept in 02-object-detection/notebooks/) point into "
                                       "the external PaddleYOLO project (yml configs and deploy docs) that "
                                       "never entered this repository",
        "problems": problems,
        "scope": "All authored Markdown and notebook markdown on both course sides; raw data, "
                 "generated outputs, virtual environments and the migration snapshot excluded.",
    }
    target = ROOT / "english/reports/docs-asset-checks.json"
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
