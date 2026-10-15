"""Framework-independent English text preparation for the training course."""
from collections import Counter
from pathlib import Path
import hashlib
import html
import json
import random
import re
import tarfile
import requests

IMDB_URL = "https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz"
CJK = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
LABELS = ["negative", "positive"]


def tokenize(text):
    """Lowercase English words; preserve internal apostrophes and negation."""
    text = html.unescape(re.sub(r"<[^>]+>", " ", text)).replace("\u2019", "'")
    return re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower())


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
        raise ValueError("A balanced subset requires at least two reviews.")
    rng = random.Random(seed)
    selected = []
    for label in (0, 1):
        group = [row for row in rows if row['label'] == label]
        rng.shuffle(group)
        selected.extend(group[:limit // 2])
    rng.shuffle(selected)
    return selected


def prepare_imdb(data_dir):
    """Download the official archive and create reproducible English JSONL splits.

    Members are read in memory, never extracted as filesystem paths. Validation
    comes only from the official training split. Exact duplicate texts are removed
    across all splits. Reviews containing CJK characters are excluded, not translated.
    """
    data_dir = Path(data_dir) / "imdb"
    data_dir.mkdir(parents=True, exist_ok=True)
    files = {name: data_dir / f"{name}.jsonl" for name in ('train', 'validation', 'test')}
    if all(p.exists() for p in files.values()):
        return files
    archive = data_dir / "aclImdb_v1.tar.gz"
    if not archive.exists():
        print("Downloading the official IMDb English movie-review dataset.")
        temporary = archive.with_suffix('.part')
        with requests.get(IMDB_URL, stream=True, timeout=90) as response, temporary.open('wb') as out:
            response.raise_for_status()
            for chunk in response.iter_content(1024 * 1024):
                if chunk:
                    out.write(chunk)
        temporary.replace(archive)
    groups = {'train': [], 'test': []}
    excluded = 0
    with tarfile.open(archive, 'r:gz') as tar:
        for member in tar:
            match = re.fullmatch(r'aclImdb/(train|test)/(neg|pos)/[^/]+\.txt', member.name)
            if not match or not member.isfile():
                continue
            text = tar.extractfile(member).read().decode('utf-8')
            text = html.unescape(re.sub(r'<[^>]+>', ' ', text))
            text = re.sub(r'\s+', ' ', text).strip()
            if CJK.search(text) or not tokenize(text):
                excluded += 1
                continue
            groups[match[1]].append({'id': member.name, 'text': text,
                                     'label': int(match[2] == 'pos')})
    # Stable ordering makes the split independent of archive member order.
    for rows in groups.values():
        rows.sort(key=lambda row: row['id'])
    seen = set()
    duplicates = 0
    for split in ('train', 'test'):
        unique = []
        for row in groups[split]:
            digest = hashlib.sha256(row['text'].encode('utf-8')).hexdigest()
            if digest in seen:
                duplicates += 1
                continue
            seen.add(digest)
            unique.append(row)
        groups[split] = unique
    train, validation = [], []
    rng = random.Random(42)
    for label in (0, 1):
        rows = [row for row in groups['train'] if row['label'] == label]
        rng.shuffle(rows)
        n_val = max(1, len(rows) // 5)
        validation.extend(rows[:n_val])
        train.extend(rows[n_val:])
    splits = {'train': train, 'validation': validation, 'test': groups['test']}
    for name, rows in splits.items():
        rng.shuffle(rows)
        temporary = files[name].with_suffix('.tmp')
        with temporary.open('w', encoding='utf-8') as out:
            for row in rows:
                out.write(json.dumps(row, ensure_ascii=False) + '\n')
        temporary.replace(files[name])
    metadata = {'source': IMDB_URL, 'seed': 42, 'excluded_non_course_texts': excluded,
                'removed_exact_duplicates': duplicates,
                'counts': {name: len(rows) for name, rows in splits.items()},
                'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}
    (data_dir / 'provenance.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print('Prepared English splits:', metadata['counts'])
    return files


def load_reviews(data_dir, split='train', limit=None):
    if split not in ('train', 'validation', 'test'):
        raise ValueError('Choose train, validation, or test.')
    path = prepare_imdb(data_dir)[split]
    rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    return balanced_subset(rows, limit)
