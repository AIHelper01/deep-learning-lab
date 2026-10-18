#!/usr/bin/env python3
"""把文档/notebook 里的远程图片下载到本地 assets，并把 assets 里的子目录展平成命名规范。

一次性迁移脚本，可重复执行：已经本地化的图片不会被再次下载，展平后的目录不会被再次移动。

- 远程图片：markdown 图片语法与 HTML `<img>` 都处理，下载到该文件所属模块（或课程路线）的
  assets；位于 `archive/` 下的文件下载到该路线的 `archive/assets/`；
  命名 `<notebook 主干|文档目录名>-<序号>.<扩展名>`，同一 URL 复用同一个本地文件；
- 子目录展平：`assets/<子目录>/<文件>` 改为 `assets/<子目录>-<序号>.<扩展名>`，并改写所有引用；
  只被归档文件引用的图片移动到 `archive/assets/`，让归档自成一体。

用法（仓库根目录）：
    ~/env_dl_uv/.venv/bin/python scripts/localize_notebook_images.py --dry-run
    ~/env_dl_uv/.venv/bin/python scripts/localize_notebook_images.py
"""
from pathlib import Path
import argparse
import os
import re
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "__pycache__", ".ipynb_checkpoints", "data", "outputs",
             "logs", "node_modules", ".pytest_cache"}
CONTAINER_DIRS = {"notebooks", "extensions", "legacy-notebooks", "archive"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
CONTENT_EXT = {"image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif",
               "image/webp": ".webp", "image/svg+xml": ".svg"}
# notebook 源码是 JSON，属性引号在文件里带反斜杠，因此正则不接受引号和反斜杠。
URL = r"(https?://[^)\\\s]+)"      # 排除右括号、反斜杠与空白（notebook JSON 里 URL 以 \" 结尾）
MD_IMAGE = re.compile(r"!\[[^\]]*\]\(" + URL)
HTML_IMAGE = re.compile(r'<img[^>]+src=\\\\?["\']?' + URL, re.I)
# 路径后必须紧跟非路径字符，避免匹配到更长的名字。
NOT_PATH = "(?=[^A-Za-z0-9._-])"
NESTED = re.compile(r"((?:\.\./)*)assets/([A-Za-z0-9._-]+)/([A-Za-z0-9._-]+\.(?:png|jpe?g|gif|webp|svg))"
                    + NOT_PATH)


def author_files():
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS or part.startswith(".venv") for part in rel.parts):
            continue
        if path.is_file() and path.suffix in {".md", ".ipynb"}:
            yield path


def assets_dir_for(path):
    """模块（或课程路线）assets；位于 archive/ 下的文件写入该路线的 archive/assets。"""
    owner = path.parent
    while owner != ROOT and owner.name in CONTAINER_DIRS:
        owner = owner.parent
    base = owner / "archive" if "archive" in path.relative_to(ROOT).parts else owner
    return base / "assets"


def prefix_for(path):
    return path.stem if path.suffix == ".ipynb" else path.parent.name


def next_index(directory, prefix):
    used = [int(candidate.stem[len(prefix) + 1:]) for candidate in directory.glob(f"{prefix}-*.*")
            if candidate.stem[len(prefix) + 1:].isdigit()]
    return max(used, default=0)


def download(url, stem):
    request = urllib.request.Request(url, headers={"User-Agent": "deep-learning-lab docs mirror"})
    with urllib.request.urlopen(request, timeout=90) as response:
        body = response.read()
        content_type = response.headers.get_content_type()
    suffix = Path(url.split("?")[0]).suffix.lower()
    if suffix not in IMAGE_SUFFIXES:
        suffix = CONTENT_EXT.get(content_type, ".png")
    target = stem.with_suffix(suffix)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(body)
    return target


def localize_images(dry_run):
    touched = 0
    for path in author_files():
        text = path.read_text(encoding="utf-8")
        urls = list(dict.fromkeys(MD_IMAGE.findall(text) + HTML_IMAGE.findall(text)))
        if not urls:
            continue
        prefix = prefix_for(path)
        assets = assets_dir_for(path)
        index = next_index(assets, prefix)
        cache = {}
        for url in urls:
            if url in cache:
                local = cache[url]
            else:
                index += 1
                stem = assets / f"{prefix}-{index}"
                if dry_run:
                    print(f"[dry-run] {url} -> {stem}-*")
                    cache[url] = Path("placeholder")
                    continue
                local = download(url, stem)
                cache[url] = local
            text = text.replace(url, Path(os.path.relpath(local, path.parent)).as_posix())
        if not dry_run:
            path.write_text(text, encoding="utf-8")
            print(f"本地化 {path.relative_to(ROOT)}：{len(urls)} 张")
        touched += 1
    return touched


def flatten_nested_assets(dry_run):
    consumers = {}
    for path in author_files():
        for _, prefix, name in NESTED.findall(path.read_text(encoding="utf-8")):
            consumers.setdefault((prefix, name), set()).add(path)
    rewritten = 0
    for assets in sorted(ROOT.rglob("assets")):
        rel = assets.relative_to(ROOT)
        if any(part in SKIP_DIRS or part.startswith(".venv") for part in rel.parts) or not assets.is_dir():
            continue
        for subdirectory in sorted(p for p in assets.iterdir() if p.is_dir()):
            prefix = subdirectory.name
            index = next_index(assets, prefix)
            for entry in sorted(subdirectory.iterdir()):
                if not entry.is_file():
                    continue
                users = consumers.get((prefix, entry.name), set())
                archived = bool(users) and all("archive" in q.relative_to(ROOT).parts for q in users)
                target_dir = (assets.parent / "archive" / "assets") if archived else assets
                index += 1
                target = target_dir / f"{prefix}-{index}{entry.suffix.lower()}"
                print(f"{subdirectory.relative_to(ROOT)}/{entry.name} -> {target.relative_to(ROOT)}"
                      + ("  (仅归档引用)" if archived else ""))
                if dry_run:
                    continue
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(entry), str(target))
                for path in sorted(users):
                    text = path.read_text(encoding="utf-8")
                    relative = Path(os.path.relpath(target, path.parent)).as_posix()
                    pattern = re.compile(r"((?:\.\./)*)" + re.escape(f"assets/{prefix}/{entry.name}") + NOT_PATH)
                    new_text = pattern.sub(relative, text)
                    if new_text != text:
                        path.write_text(new_text, encoding="utf-8")
                        rewritten += 1
            if not dry_run and subdirectory.exists() and not any(subdirectory.iterdir()):
                subdirectory.rmdir()
    return rewritten


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    localize_images(args.dry_run)
    flatten_nested_assets(args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
