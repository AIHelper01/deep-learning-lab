"""中文文本课程的数据准备：ChnSentiCorp 酒店评论 + jieba 分词。

接口与 english/common/course_data.py 保持一致（load_reviews / tokenize /
build_vocab / encode / LABELS），因此中文课程与英文课程的单元结构可以一一对应。

划分口径（写入 provenance.json，可复核）：
- train / validation：官方 train.tsv（9600 条，带标签），按标签各取 20% 作为验证集；
- test：官方 dev.tsv（1200 条，带标签）。本发行包里的 test.tsv 只有 qid 和文本、
  没有标签，是排行榜用的隐藏测试集，因此本课程的最终评测使用带标签的 dev.tsv。
"""
from collections import Counter
from pathlib import Path
import csv
import hashlib
import json
import random
import re
import zipfile

import requests

CHNSENTICORP_URL = "https://bj.bcebos.com/paddlenlp/datasets/ChnSentiCorp.zip"
LABELS = ["负面", "正面"]
CJK = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
LATIN = re.compile(r"[a-z0-9]+")

_JIEBA = None


def _jieba():
    global _JIEBA
    if _JIEBA is None:
        import jieba

        jieba.setLogLevel(60)
        _JIEBA = jieba
    return _JIEBA


def tokenize(text):
    """中文按词切分（jieba），保留英文与数字词；不做停用词表裁剪。"""
    text = (text or "").strip().lower()
    if not text:
        return []
    words = []
    for token in _jieba().cut(text, HMM=False):
        token = token.strip()
        if not token:
            continue
        if CJK.search(token) or LATIN.fullmatch(token):
            words.append(token)
    return words


def build_vocab(texts, max_words=20000, min_freq=2):
    counts = Counter(word for text in texts for word in tokenize(text))
    words = sorted(counts, key=lambda word: (-counts[word], word))
    vocab = {"<pad>": 0, "<unk>": 1}
    for word in words:
        if counts[word] >= min_freq and len(vocab) < max_words:
            vocab[word] = len(vocab)
    return vocab


def encode(text, vocab, max_length=200):
    ids = [vocab.get(word, 1) for word in tokenize(text)][:max_length] or [1]
    length = len(ids)
    return ids + [0] * (max_length - length), length


def balanced_subset(rows, limit, seed=42):
    if limit is None or limit >= len(rows):
        return list(rows)
    if limit < 2:
        raise ValueError("平衡子集至少需要两条评论。")
    rng = random.Random(seed)
    selected = []
    for label in (0, 1):
        group = [row for row in rows if row["label"] == label]
        rng.shuffle(group)
        selected.extend(group[: limit // 2])
    rng.shuffle(selected)
    return selected


def _read_tsv(path):
    """读取 ChnSentiCorp 的 TSV；自动识别 label 所在列，跳过表头。"""
    rows = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader, None)
        if header is None:
            return rows
        names = [name.strip().lower() for name in header]
        if "label" in names and "text_a" in names:
            label_index, text_index = names.index("label"), names.index("text_a")
        elif names[:2] == ["qid", "label"] or (len(names) > 2 and "qid" in names):
            label_index, text_index = 1, 2
        else:
            label_index, text_index = 0, 1
        for fields in reader:
            if len(fields) <= max(label_index, text_index):
                continue
            try:
                label = int(fields[label_index])
            except ValueError:
                continue
            if label not in (0, 1):
                continue
            rows.append({"text": re.sub(r"\s+", " ", fields[text_index]).strip(),
                         "label": label})
    return rows


def _source_dir(data_dir):
    source = Path(data_dir) / "ChnSentiCorp"
    if (source / "train.tsv").is_file():
        return source
    archive = Path(data_dir) / "ChnSentiCorp.zip"
    if not archive.exists():
        print("正在下载中文情感分析数据集 ChnSentiCorp。")
        temporary = archive.with_suffix(".part")
        with requests.get(CHNSENTICORP_URL, stream=True, timeout=120) as response, temporary.open("wb") as out:
            response.raise_for_status()
            for chunk in response.iter_content(1024 * 1024):
                if chunk:
                    out.write(chunk)
        temporary.replace(archive)
    with zipfile.ZipFile(archive) as package:
        package.extractall(Path(data_dir))
    for candidate in (source, Path(data_dir) / "ChnSentiCorp" / "ChnSentiCorp"):
        if (candidate / "train.tsv").is_file():
            return candidate
    raise FileNotFoundError("未找到 ChnSentiCorp/train.tsv，请先按 data/README.md 放置数据集。")


def prepare_chnsentiment(data_dir):
    """生成可复现的中文 JSONL 划分，并写出 provenance.json。"""
    data_dir = Path(data_dir)
    target = data_dir / "chnsentiment"
    target.mkdir(parents=True, exist_ok=True)
    files = {name: target / f"{name}.jsonl" for name in ("train", "validation", "test")}
    if all(path.exists() for path in files.values()):
        return files
    source = _source_dir(data_dir)
    official_train = _read_tsv(source / "train.tsv")
    official_dev = _read_tsv(source / "dev.tsv")

    def clean(rows, split):
        kept, dropped = [], 0
        for position, row in enumerate(rows):
            if not CJK.search(row["text"]) or not tokenize(row["text"]):
                dropped += 1
                continue
            kept.append({"id": f"{split}-{position:05d}", "text": row["text"],
                         "label": row["label"]})
        return kept, dropped

    train_rows, dropped_train = clean(official_train, "train")
    test_rows, dropped_test = clean(official_dev, "dev")

    seen, duplicates = set(), 0
    def deduplicate(rows):
        nonlocal duplicates
        unique = []
        for row in rows:
            digest = hashlib.sha256(row["text"].encode("utf-8")).hexdigest()
            if digest in seen:
                duplicates += 1
                continue
            seen.add(digest)
            unique.append(row)
        return unique

    train_rows, test_rows = deduplicate(train_rows), deduplicate(test_rows)
    train_rows.sort(key=lambda row: row["id"])
    test_rows.sort(key=lambda row: row["id"])

    rng = random.Random(42)
    train, validation = [], []
    for label in (0, 1):
        rows = [row for row in train_rows if row["label"] == label]
        rng.shuffle(rows)
        n_val = max(1, len(rows) // 5)
        validation.extend(rows[:n_val])
        train.extend(rows[n_val:])
    splits = {"train": train, "validation": validation, "test": test_rows}
    for name, rows in splits.items():
        rng.shuffle(rows)
        temporary = files[name].with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as out:
            for row in rows:
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary.replace(files[name])
    metadata = {
        "source": CHNSENTICORP_URL,
        "seed": 42,
        "labels": LABELS,
        "tokenizer": "jieba (word level, no stopword list)",
        "splits": {
            "train": "official train.tsv minus 20% per label",
            "validation": "20% per label drawn from official train.tsv",
            "test": "official dev.tsv (labelled); shipped test.tsv has no labels",
        },
        "excluded_rows": {"train": dropped_train, "dev": dropped_test},
        "removed_exact_duplicates": duplicates,
        "counts": {name: len(rows) for name, rows in splits.items()},
        "source_sha256": {name: hashlib.sha256((source / f"{name}.tsv").read_bytes()).hexdigest()
                          for name in ("train", "dev") if (source / f"{name}.tsv").is_file()},
    }
    (target / "provenance.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2),
                                            encoding="utf-8")
    print("已生成中文数据划分：", metadata["counts"])
    return files


def load_reviews(data_dir, split="train", limit=None):
    if split not in ("train", "validation", "test"):
        raise ValueError("请选择 train、validation 或 test。")
    path = prepare_chnsentiment(data_dir)[split]
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    return balanced_subset(rows, limit)
