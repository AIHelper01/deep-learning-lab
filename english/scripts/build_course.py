"""Author the English teaching notebooks. Run before editing generated notebooks."""
from pathlib import Path
import json
import textwrap
import uuid

ROOT = Path(__file__).resolve().parents[1]


def write(path, content):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + '\n', encoding='utf-8')


def markdown_source(source):
    """Dedent lesson prose that was authored inside an indented call.

    ``textwrap.dedent`` finds no common prefix when the opening line sits on the same line as the
    opening quotes, which left the whole body indented by four spaces - Jupyter then renders
    explanatory prose as a code block. The first line (a title or heading) stays flush and the rest
    lose only their shared indentation, so nested lists and fenced code keep their own indentation.
    """
    lines = textwrap.dedent(source).strip().split("\n")
    body = [line for line in lines[1:] if line.strip()]
    if body:
        width = min(len(line) - len(line.lstrip(" ")) for line in body)
        if width:
            prefix = " " * width
            lines = [lines[0]] + [line[len(prefix):] if line.startswith(prefix) else line
                                  for line in lines[1:]]
    return "\n".join(lines).splitlines(keepends=True)


def md(source):
    return {'cell_type': 'markdown', 'id': uuid.uuid4().hex[:8], 'metadata': {},
            'source': markdown_source(source)}


def code(source):
    return {'cell_type': 'code', 'id': uuid.uuid4().hex[:8], 'metadata': {},
            'execution_count': None, 'outputs': [],
            'source': textwrap.dedent(source).strip().splitlines(keepends=True)}


def notebook(path, cells):
    nb = {'cells': cells, 'metadata': {'kernelspec': {'display_name': 'Python 3',
          'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'},
          'course': {'language': 'en', 'edition': '2026-10-15'}},
          'nbformat': 4, 'nbformat_minor': 5}
    write(path, json.dumps(nb, ensure_ascii=False, indent=1))


BOOT = '''
from pathlib import Path
import os
import sys

# Find the English course root without relying on a specific working directory.
start = Path.cwd().resolve()
COURSE = next((p for p in [start, *start.parents]
               if (p / "COURSE_ROOT").is_file()), None)
if COURSE is None and (start / "english" / "COURSE_ROOT").is_file():
    COURSE = start / "english"
if COURSE is None:
    raise RuntimeError("Start Jupyter inside the project or the english directory.")
sys.path.insert(0, str(COURSE / "common"))
os.environ.setdefault("HF_HOME", str(COURSE / "data" / "huggingface"))
os.environ.setdefault("TORCH_HOME", str(COURSE / "data" / "torch-cache"))
'''

CV_SETUP = '''
import random
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Subset, random_split
from torchvision import datasets, transforms, models
import matplotlib.pyplot as plt

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.set_num_threads(2)
DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
DATA = COURSE / "01-image-classification" / "data"
OUTPUT = COURSE / "01-image-classification" / "outputs" / EXPERIMENT
DATA.mkdir(parents=True, exist_ok=True)
OUTPUT.mkdir(parents=True, exist_ok=True)
SMOKE = os.environ.get("COURSE_SMOKE", "0") == "1"
EPOCHS = 1 if SMOKE else 3
BATCH_SIZE = 32 if SMOKE else 64
print(f"Device: {DEVICE}; experiment: {EXPERIMENT}; smoke test: {SMOKE}")
'''

LENET = '''
class LeNet(nn.Module):
    def __init__(self, in_channels=1, image_size=28, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_channels, 6, kernel_size=5, padding=2), nn.ReLU(),
            nn.AvgPool2d(2), nn.Conv2d(6, 16, kernel_size=5), nn.ReLU(),
            nn.AvgPool2d(2), nn.Flatten())
        with torch.no_grad():
            width = self.features(torch.zeros(1, in_channels, image_size, image_size)).shape[1]
        self.classifier = nn.Sequential(nn.Linear(width, 120), nn.ReLU(),
                                        nn.Linear(120, 84), nn.ReLU(),
                                        nn.Linear(84, num_classes))

    def forward(self, images):
        return self.classifier(self.features(images))

model = LeNet(CHANNELS, IMAGE_SIZE, len(CLASS_NAMES)).to(DEVICE)
print("Logit shape:", tuple(model(torch.zeros(2, CHANNELS, IMAGE_SIZE, IMAGE_SIZE, device=DEVICE)).shape))
'''

CV_LOOP = '''
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam((p for p in model.parameters() if p.requires_grad), lr=0.001)

def run_epoch(loader, training=False):
    model.train(training)
    total_loss, correct, count = 0.0, 0, 0
    with torch.set_grad_enabled(training):
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            if training:
                optimizer.zero_grad()
            logits = model(images)
            loss = criterion(logits, labels)
            if training:
                loss.backward()
                optimizer.step()
            total_loss += loss.item() * len(labels)
            correct += (logits.argmax(1) == labels).sum().item()
            count += len(labels)
    return total_loss / count, correct / count

history, best_accuracy = [], -1.0
checkpoint = OUTPUT / "best_model.pt"
for epoch in range(EPOCHS):
    train_loss, train_accuracy = run_epoch(train_loader, training=True)
    val_loss, val_accuracy = run_epoch(val_loader)
    history.append([train_loss, val_loss, train_accuracy, val_accuracy])
    if val_accuracy > best_accuracy:
        best_accuracy = val_accuracy
        torch.save(model.state_dict(), checkpoint)
    print(f"Epoch {epoch + 1}/{EPOCHS} | train loss {train_loss:.4f} | "
          f"validation loss {val_loss:.4f} | validation accuracy {val_accuracy:.3f}")
'''

CV_EVAL = '''
import json
model.load_state_dict(torch.load(checkpoint, map_location=DEVICE, weights_only=True))
test_loss, test_accuracy = run_epoch(test_loader)
print(f"Held-out test accuracy: {test_accuracy:.3f}")
metrics = {"test_accuracy": test_accuracy, "test_loss": test_loss,
           "best_validation_accuracy": best_accuracy, "seed": SEED,
           "smoke_test": SMOKE, "epochs": EPOCHS, "classes": CLASS_NAMES}
(OUTPUT / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

fig, axes = plt.subplots(1, 2, figsize=(10, 3))
values = np.asarray(history)
axes[0].plot(values[:, 0], label="Training")
axes[0].plot(values[:, 1], label="Validation")
axes[0].set(title="Cross-entropy loss", xlabel="Epoch", ylabel="Loss")
axes[1].plot(values[:, 2], label="Training")
axes[1].plot(values[:, 3], label="Validation")
axes[1].set(title="Classification accuracy", xlabel="Epoch", ylabel="Accuracy")
for axis in axes:
    axis.legend()
fig.tight_layout()
fig.savefig(OUTPUT / "training_curves.png")
plt.show()
'''

CV_ERRORS = '''
confusion = np.zeros((len(CLASS_NAMES), len(CLASS_NAMES)), dtype=int)
mistakes = []
model.eval()
with torch.no_grad():
    for images, labels in test_loader:
        predictions = model(images.to(DEVICE)).argmax(1).cpu()
        for image, true, predicted in zip(images, labels, predictions):
            confusion[int(true), int(predicted)] += 1
            if true != predicted and len(mistakes) < 6:
                mistakes.append((image, int(true), int(predicted)))
fig, axis = plt.subplots(figsize=(7, 6))
axis.imshow(confusion, cmap="Blues")
axis.set(xticks=range(len(CLASS_NAMES)), yticks=range(len(CLASS_NAMES)),
         xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES,
         xlabel="Predicted class", ylabel="True class", title="Test confusion matrix")
plt.setp(axis.get_xticklabels(), rotation=45, ha="right")
fig.tight_layout()
fig.savefig(OUTPUT / "confusion_matrix.png")
plt.show()
for _, true, predicted in mistakes:
    print(f"Misclassified example: true={CLASS_NAMES[true]}, predicted={CLASS_NAMES[predicted]}")

# Single-image inference uses the same preprocessing as evaluation.
image, true_label = test_set[0]
with torch.no_grad():
    probabilities = model(image.unsqueeze(0).to(DEVICE)).softmax(1)[0].cpu()
prediction = int(probabilities.argmax())
print(f"Prediction: {CLASS_NAMES[prediction]} | confidence: {probabilities[prediction]:.3f} | "
      f"true label: {CLASS_NAMES[int(true_label)]}")
'''


def cv_notebook(path, title, experiment, dataset='mnist', custom=False, compact=False):
    cells = [md(f'''# {title}

    **Learning outcomes:** prepare a reproducible dataset, inspect tensor shapes,
    train a classifier, select a checkpoint using validation data, and evaluate on
    a separate test set. All class names and plots in this edition are in English.

    Run cells from top to bottom. The first dataset/model download requires internet.
    CPU mode works; set `COURSE_SMOKE=1` before starting the kernel for a short pipeline check.
    A smoke-test score is not a measure of model quality.
    '''), code(BOOT), code(f'EXPERIMENT = "{experiment}"\n'+CV_SETUP)]
    if custom:
        cells += [md('''## 1. Build your own folder dataset

        The original custom-data lesson requires an unavailable LEDNUM collection.
        Here we preserve the custom digit-classification workflow by exporting MNIST
        to `train/zero`, `train/one`, ... folders. This is handwritten-digit data, not
        LED-display data; it demonstrates dataset indexing, not LED-domain accuracy.
        Real custom images can replace these files if the same split and class layout
        is retained. Split by writer/source when multiple images share an origin.
        '''), code('''
        CLASS_NAMES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
        CHANNELS, IMAGE_SIZE = 1, 28
        source_train = datasets.MNIST(DATA, train=True, download=True)
        source_test = datasets.MNIST(DATA, train=False, download=True)
        folder = DATA / ("custom-digits-balanced-smoke" if SMOKE else "custom-digits-balanced")
        import csv
        # Stable source indices keep exported train and validation images disjoint.
        for split, source, start_index, end_index, per_class in [
            ("train", source_train, 0, 50000, 6 if SMOKE else 200),
            ("validation", source_train, 50000, 60000, 3 if SMOKE else 50),
            ("test", source_test, 0, 10000, 3 if SMOKE else 50)]:
            for name in CLASS_NAMES:
                (folder / split / name).mkdir(parents=True, exist_ok=True)
            rows = []
            # Select every class explicitly, including in a tiny smoke run.
            selected = []
            for category in range(len(CLASS_NAMES)):
                candidates = [i for i in range(start_index, end_index)
                              if int(source.targets[i]) == category]
                selected.extend(candidates[:per_class])
            for index in selected:
                image, label = source[index]
                target = folder / split / CLASS_NAMES[label] / f"digit_{index:05d}.png"
                if not target.exists():
                    image.save(target)
                rows.append([target.relative_to(folder).as_posix(), CLASS_NAMES[label]])
            with (folder / f"{split}.csv").open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["image_path", "label"])
                writer.writerows(rows)

        transform = transforms.Compose([transforms.Grayscale(), transforms.ToTensor(),
                                        transforms.Normalize((0.1307,), (0.3081,))])
        train_set = datasets.ImageFolder(folder / "train", transform=transform)
        val_set = datasets.ImageFolder(folder / "validation", transform=transform)
        test_set = datasets.ImageFolder(folder / "test", transform=transform)
        # ImageFolder sorts folder names alphabetically; do not assume numeric order.
        CLASS_NAMES = train_set.classes
        assert train_set.class_to_idx == val_set.class_to_idx == test_set.class_to_idx
        print("Folder label mapping:", train_set.class_to_idx)
        ''')]
    else:
        mnist = dataset == 'mnist'
        cells += [md('''## 1. Prepare training, validation, and test data

        Keep the official test split untouched until final evaluation. Create validation
        data only from the training split. The fixed seed controls the split. A classroom
        run uses a subset to keep runtime manageable; increase limits for a fuller experiment.
        '''), code(textwrap.dedent(('''
        CLASS_NAMES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
        CHANNELS, IMAGE_SIZE = 1, 28
        transform = transforms.Compose([transforms.ToTensor(),
                                        transforms.Normalize((0.1307,), (0.3081,))])
        full_train = datasets.MNIST(DATA, train=True, download=True, transform=transform)
        test_set = datasets.MNIST(DATA, train=False, download=True, transform=transform)
        ''' if mnist else '''
        CLASS_NAMES = ["airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"]
        CHANNELS, IMAGE_SIZE = 3, 32
        transform = transforms.Compose([transforms.ToTensor(),
                                        transforms.Normalize((0.5,)*3, (0.5,)*3)])
        from vision_data import load_cifar10
        full_train = load_cifar10(DATA / "cifar10", train=True, transform=transform)
        test_set = load_cifar10(DATA / "cifar10", train=False, transform=transform)
        ''')) + textwrap.dedent('''
        val_size = len(full_train) // 10
        train_set, val_set = random_split(full_train, [len(full_train) - val_size, val_size],
                                          generator=torch.Generator().manual_seed(SEED))
        train_set = Subset(train_set, range(min(len(train_set), 64 if SMOKE else 4000)))
        val_set = Subset(val_set, range(min(len(val_set), 32 if SMOKE else 1000)))
        test_set = Subset(test_set, range(min(len(test_set), 32 if SMOKE else 1000)))
        '''))]
    cells += [code('''
    train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True, num_workers=0,
                              generator=torch.Generator().manual_seed(SEED))
    val_loader = DataLoader(val_set, batch_size=BATCH_SIZE, num_workers=0)
    test_loader = DataLoader(test_set, batch_size=BATCH_SIZE, num_workers=0)
    images, labels = next(iter(train_loader))
    print("Batch shape:", tuple(images.shape), "Label shape:", tuple(labels.shape))
    print("Split sizes:", len(train_set), len(val_set), len(test_set))
    fig, axes = plt.subplots(1, 6, figsize=(10, 2))
    for axis, image, label in zip(axes, images, labels):
        view = image[0] if CHANNELS == 1 else image.permute(1, 2, 0)
        view = (view - view.min()) / (view.max() - view.min() + 1e-8)
        axis.imshow(view, cmap="gray" if CHANNELS == 1 else None)
        axis.set_title(CLASS_NAMES[int(label)])
        axis.axis("off")
    fig.suptitle("Training examples")
    plt.show()
    '''), md('''## 2. Define the model

    A convolution learns local features with shared weights. Pooling reduces spatial
    size; the final linear layer returns one logit per class. Cross-entropy expects
    logits, so softmax is used only when displaying prediction probabilities.
    '''), code(LENET), md('''## 3. Train and select a checkpoint

    Training enables gradients and updates parameters. Evaluation disables gradients
    and switches dropout/batch normalization to evaluation behavior. Save the checkpoint
    with the highest validation accuracy; never choose it using test accuracy.
    '''), code(CV_LOOP), md('## 4. Evaluate the saved checkpoint'), code(CV_EVAL)]
    if not compact:
        cells += [md('## 5. Inspect errors and predict one image'), code(CV_ERRORS)]
    cells += [md('''## Exercises and discussion

    1. Predict each tensor shape before running the model.
    2. Compare learning rates while keeping the split fixed.
    3. Explain why validation and test results can differ.
    4. Inspect misclassified examples before increasing model size.
    5. For a new image, apply exactly the evaluation preprocessing and class mapping.

    The model weights, class names, seed, and metrics are stored under this experiment's
    output directory. Results depend on the subset, hardware, and training duration.
    ''')]
    if dataset == 'resnet':
        # Replace the data transform and network, preserving the teaching workflow.
        for c in cells:
            if c['cell_type'] != 'code': continue
            s = ''.join(c['source'])
            if 'full_train = load_cifar10' in s:
                s = s.replace('CHANNELS, IMAGE_SIZE = 3, 32', 'CHANNELS, IMAGE_SIZE = 3, 224')
                s = s.replace('transform = transforms.Compose([transforms.ToTensor(),\n',
                              'transform = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(),\n')
                s = s.replace('transforms.Normalize((0.5,)*3, (0.5,)*3)',
                              'transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))')
            if 'class LeNet(' in s:
                s = textwrap.dedent('''
                # Smoke mode checks wiring without downloading pretrained weights.
                weights = None if SMOKE else models.ResNet18_Weights.DEFAULT
                model = models.resnet18(weights=weights)
                for parameter in model.parameters():
                    parameter.requires_grad = False
                model.fc = nn.Linear(model.fc.in_features, len(CLASS_NAMES))
                model = model.to(DEVICE)
                print("Trainable parameters:", sum(p.numel() for p in model.parameters() if p.requires_grad))
                ''').strip()
            if 'def run_epoch' in s:
                s = s.replace('model.train(training)', 'model.eval()  # Keep frozen backbone batch statistics fixed.\n    model.fc.train(training)')
            c['source'] = s.splitlines(keepends=True)
        cells.insert(7, md('''### Transfer learning with ResNet18

        Residual connections add an identity shortcut to learned transformations.
        This lesson freezes the pretrained backbone and trains a new ten-class head.
        Batch-normalization statistics also stay fixed. Use ImageNet normalization;
        input images are resized to 224 by 224. A smoke run uses random weights and
        cannot demonstrate transfer-learning performance.
        '''))
    notebook(path, cells)


def overview(framework):
    notebook(f'03-sentiment-analysis/{framework}/notebooks/01-nlp-overview.ipynb', [
        md('''# Natural Language Processing: an English-language introduction

        **Learning outcomes:** distinguish NLP tasks, explain tokenization and ambiguity,
        and define a binary sentiment-classification experiment.

        | Task | English example | Output |
        |---|---|---|
        | Sentiment analysis | "The film was surprisingly good." | positive |
        | Named-entity recognition | "Alex visited London." | person, location |
        | Semantic similarity | "A lovely film" / "An excellent movie" | similarity score |
        | Question answering | "Who directed the film?" | an answer span |
        | Text generation | "Write a short review." | generated text |
        '''), md('''## Why language is difficult

        "Not bad" is not the same as "bad". "Great, another delay" may be sarcastic.
        "The bank is closed" needs context. Word order, negation, domain, and document
        length all affect meaning. Positive and negative are dataset labels, not a
        complete description of every real review; mixed and neutral cases still exist.

        English words are separated by spaces much of the time, but contractions,
        punctuation, and names still need a tokenization policy. This course preserves
        apostrophes and negation using a small regular-expression tokenizer. Production
        transformer models use their own subword tokenizer instead.
        '''), code(BOOT), code('''
        from course_data import tokenize
        examples = ["I loved the acting, but the ending was disappointing.",
                    "The movie isn't bad at all.", "Great, another predictable ending."]
        for text in examples:
            print("Text:", text)
            print("Tokens:", tokenize(text))
        '''), md('''## Our experiment

        We use the [Stanford IMDb movie-review dataset](https://ai.stanford.edu/~amaas/data/sentiment/).
        Labels are `negative=0` and `positive=1`. A validation split is drawn from the
        official training data; the official test split is reserved for final evaluation.
        The preparation code filters reviews containing CJK characters and removes exact
        duplicate text across splits, so prepared counts can differ from published counts.

        Vocabulary construction and Word2Vec fitting use training text only. Validation
        and test words outside that vocabulary map to an unknown token. A pretrained
        sentiment model is an optional separate comparison, not the LSTM being trained.

        **Discuss:** How would you label a mixed review? Why should a negation word remain
        in the input? Why is accuracy on a tiny classroom subset not a benchmark result?
        ''')])


TEXT_SETUP = '''
import json
import random
import numpy as np
from course_data import load_reviews, tokenize, build_vocab, encode, LABELS

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
SMOKE = os.environ.get("COURSE_SMOKE", "0") == "1"
DATA = COURSE / "03-sentiment-analysis" / "data"
OUTPUT = COURSE / "03-sentiment-analysis" / "outputs" / FRAMEWORK / EXPERIMENT
OUTPUT.mkdir(parents=True, exist_ok=True)
train_rows = load_reviews(DATA, "train", 64 if SMOKE else 4000)
validation_rows = load_reviews(DATA, "validation", 32 if SMOKE else 1000)
test_rows = load_reviews(DATA, "test", 32 if SMOKE else 1000)
print("Split sizes:", len(train_rows), len(validation_rows), len(test_rows))
print("Labels:", LABELS)
'''


def embeddings(framework):
    cells = [md('''# Word embeddings: from English words to vectors

    **Learning outcomes:** compare one-hot vectors and dense embeddings, train Skip-gram
    vectors using training reviews only, and compute word/sentence similarity.

    One-hot vectors identify words but do not express similarity. Word2Vec learns from
    nearby words: CBOW predicts a center word from context; Skip-gram predicts context
    from a center word. Similar context can make antonyms close, so cosine similarity
    is not a sentiment classifier. Small training subsets give unstable neighbors.
    '''), code(BOOT), code(f'FRAMEWORK = "{framework}"\nEXPERIMENT = "word-embeddings"\n'+TEXT_SETUP),
    md('## 1. Train Word2Vec on training reviews'), code('''
    from gensim.models import Word2Vec
    sentences = [tokenize(row["text"]) for row in train_rows]
    word2vec = Word2Vec(sentences=sentences, vector_size=64, window=5,
                        min_count=1 if SMOKE else 2, sg=1, workers=1,
                        epochs=1 if SMOKE else 5, seed=SEED)
    words = word2vec.wv.index_to_key
    vectors = word2vec.wv.vectors.copy()
    print("Vocabulary size:", len(words), "Vector shape:", vectors.shape)
    word2vec.save(str(OUTPUT / "english_word2vec.model"))
    '''), md('''## 2. Load vectors into the framework's embedding layer

    The row index is the token ID. We copy the learned vectors and freeze them for this
    demonstration. In a downstream classifier you can choose to fine-tune them.
    '''), code('''
    import torch
    embedding = torch.nn.Embedding.from_pretrained(torch.tensor(vectors), freeze=True)
    word_to_id = {word: index for index, word in enumerate(words)}
    example_word = "movie" if "movie" in word_to_id else words[0]
    vector = embedding(torch.tensor([word_to_id[example_word]])).detach().numpy()[0]
    print(f"Embedding for '{example_word}': shape={vector.shape}")
    ''' if framework=='pytorch' else '''
    import paddle
    embedding = paddle.nn.Embedding(len(words), vectors.shape[1])
    embedding.weight.set_value(vectors)
    embedding.weight.stop_gradient = True
    word_to_id = {word: index for index, word in enumerate(words)}
    example_word = "movie" if "movie" in word_to_id else words[0]
    vector = embedding(paddle.to_tensor([word_to_id[example_word]], dtype="int64")).numpy()[0]
    print(f"Embedding for '{example_word}': shape={vector.shape}")
    '''), md('## 3. Explore word and sentence similarity'), code('''
    print("Nearest words:", word2vec.wv.most_similar(example_word, topn=min(5, len(words)-1)))

    def sentence_vector(text):
        known = [word2vec.wv[word] for word in tokenize(text) if word in word2vec.wv]
        return np.mean(known, axis=0) if known else np.zeros(64, dtype=np.float32)

    def cosine(a, b):
        return float(np.dot(a, b) / max(np.linalg.norm(a) * np.linalg.norm(b), 1e-8))

    first = "The movie was enjoyable and the acting was excellent."
    second = "I liked the film and its performances."
    print("Sentence similarity:", cosine(sentence_vector(first), sentence_vector(second)))
    print("Try comparing 'good' and 'not good'; average vectors can lose word order.")
    '''), md('''## 4. Visualize a projection

    This two-dimensional PCA projection is a lossy view of the embedding space.
    Nearby points on the chart do not prove semantic equivalence.
    '''), code('''
    import matplotlib.pyplot as plt
    chosen = words[:min(30, len(words))]
    matrix = np.stack([word2vec.wv[word] for word in chosen])
    centered = matrix - matrix.mean(axis=0)
    _, _, axes = np.linalg.svd(centered, full_matrices=False)
    points = centered @ axes[:2].T
    fig, axis = plt.subplots(figsize=(10, 6))
    axis.scatter(points[:, 0], points[:, 1])
    for word, (x, y) in zip(chosen, points):
        axis.annotate(word, (x, y), fontsize=9)
    axis.set(title="English word vectors: PCA projection", xlabel="Principal component 1",
             ylabel="Principal component 2")
    fig.tight_layout()
    fig.savefig(OUTPUT / "word_vectors.png")
    plt.show()
    '''), md('''## Exercises

    Compare CBOW (`sg=0`) and Skip-gram (`sg=1`). Increase training data before interpreting
    neighbors. Test an unknown word and explain why it has no trained vector. Compare
    sentence averaging with an order-sensitive LSTM in the next lesson.
    ''')]
    notebook(f'03-sentiment-analysis/{framework}/notebooks/02-word-embeddings.ipynb',cells)


TORCH_TEXT = '''
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from torch.nn.utils.rnn import pack_padded_sequence

torch.manual_seed(SEED)
torch.set_num_threads(2)
DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)

def make_loader(rows, shuffle=False):
    encoded = [encode(row["text"], vocab, MAX_LENGTH) for row in rows]
    ids = torch.tensor([item[0] for item in encoded], dtype=torch.long)
    lengths = torch.tensor([item[1] for item in encoded], dtype=torch.long)
    labels = torch.tensor([row["label"] for row in rows], dtype=torch.long)
    return DataLoader(TensorDataset(ids, lengths, labels), batch_size=32,
                      shuffle=shuffle, num_workers=0,
                      generator=torch.Generator().manual_seed(SEED))

class SentimentLSTM(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, 64, padding_idx=0)
        self.lstm = nn.LSTM(64, 64, batch_first=True, bidirectional=True)
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(128, 2)

    def forward(self, ids, lengths):
        embedded = self.embedding(ids)
        # Ignore right-padding when computing the final states in both directions.
        packed = pack_padded_sequence(embedded, lengths.cpu(), batch_first=True,
                                       enforce_sorted=False)
        _, (hidden, _) = self.lstm(packed)
        return self.classifier(self.dropout(torch.cat([hidden[-2], hidden[-1]], dim=1)))

model = SentimentLSTM(len(vocab)).to(DEVICE)
train_loader = make_loader(train_rows, True)
validation_loader = make_loader(validation_rows)
test_loader = make_loader(test_rows)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

def run_epoch(loader, training=False):
    model.train(training)
    loss_total, correct, count = 0.0, 0, 0
    with torch.set_grad_enabled(training):
        for ids, lengths, labels in loader:
            ids, labels = ids.to(DEVICE), labels.to(DEVICE)
            if training:
                optimizer.zero_grad()
            logits = model(ids, lengths)
            loss = criterion(logits, labels)
            if training:
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
            loss_total += loss.item() * len(labels)
            correct += (logits.argmax(1) == labels).sum().item()
            count += len(labels)
    return loss_total / count, correct / count

def save_weights(path):
    torch.save(model.state_dict(), path)

def load_weights(path):
    model.load_state_dict(torch.load(path, map_location=DEVICE, weights_only=True))

def predict(texts):
    encoded = [encode(text, vocab, MAX_LENGTH) for text in texts]
    ids = torch.tensor([item[0] for item in encoded], device=DEVICE)
    lengths = torch.tensor([item[1] for item in encoded])
    model.eval()
    with torch.no_grad():
        return model(ids, lengths).softmax(1).cpu().numpy()
'''

PADDLE_TEXT = '''
import paddle
from paddle import nn

paddle.seed(SEED)
paddle.set_device("gpu" if paddle.is_compiled_with_cuda() else "cpu")

class ReviewDataset(paddle.io.Dataset):
    def __init__(self, rows):
        super().__init__()
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        ids, length = encode(row["text"], vocab, MAX_LENGTH)
        return np.asarray(ids, dtype="int64"), np.int64(length), np.int64(row["label"])

def make_loader(rows, shuffle=False):
    return paddle.io.DataLoader(ReviewDataset(rows), batch_size=32, shuffle=shuffle,
                                num_workers=0, return_list=True)

class SentimentLSTM(nn.Layer):
    def __init__(self, vocab_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, 64, padding_idx=0)
        self.lstm = nn.LSTM(64, 64, direction="bidirectional")
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(128, 2)

    def forward(self, ids, lengths):
        embedded = self.embedding(ids)
        # sequence_length prevents padding from becoming part of the final state.
        _, (hidden, _) = self.lstm(embedded, sequence_length=lengths)
        return self.classifier(self.dropout(paddle.concat([hidden[-2], hidden[-1]], axis=1)))

model = SentimentLSTM(len(vocab))
train_loader = make_loader(train_rows, True)
validation_loader = make_loader(validation_rows)
test_loader = make_loader(test_rows)
criterion = nn.CrossEntropyLoss()
optimizer = paddle.optimizer.Adam(learning_rate=0.001, parameters=model.parameters(),
                                  grad_clip=nn.ClipGradByGlobalNorm(1.0))

def run_epoch(loader, training=False):
    model.train() if training else model.eval()
    loss_total, correct, count = 0.0, 0, 0
    with paddle.set_grad_enabled(training):
        for ids, lengths, labels in loader:
            if training:
                optimizer.clear_grad()
            logits = model(ids, lengths)
            loss = criterion(logits, labels)
            if training:
                loss.backward()
                optimizer.step()
            size = int(labels.shape[0])
            loss_total += float(loss.item()) * size
            correct += int((logits.argmax(axis=1) == labels).astype("int64").sum().item())
            count += size
    return loss_total / count, correct / count

def save_weights(path):
    paddle.save(model.state_dict(), str(path))

def load_weights(path):
    model.set_state_dict(paddle.load(str(path)))

def predict(texts):
    encoded = [encode(text, vocab, MAX_LENGTH) for text in texts]
    ids = paddle.to_tensor([item[0] for item in encoded], dtype="int64")
    lengths = paddle.to_tensor([item[1] for item in encoded], dtype="int64")
    model.eval()
    with paddle.no_grad():
        return paddle.nn.functional.softmax(model(ids, lengths), axis=1).numpy()
'''


def sentiment(framework):
    cells=[md('''# English movie-review sentiment classification with a bidirectional LSTM

    **Learning outcomes:** build a vocabulary from training data, encode and pad reviews,
    train an order-sensitive model, select a validation checkpoint, and predict English labels.

    This lesson uses IMDb movie reviews instead of Chinese hotel reviews. It uses an
    English tokenizer rather than Chinese word segmentation. Both framework editions
    share the same prepared data and label mapping, but have separate environments and outputs.
    '''),code(BOOT),code(f'FRAMEWORK = "{framework}"\nEXPERIMENT = "lstm-sentiment"\n'+TEXT_SETUP),
    md('''## 1. Build a vocabulary without test leakage

    `<pad>` is ID 0; `<unk>` is ID 1. Truncate very long reviews for the classroom
    experiment and track true lengths. The vocabulary is fitted on training text only.
    Do not remove "not" or other negation words as stopwords.
    '''),code('''
    MAX_LENGTH = 40 if SMOKE else 200
    vocab = build_vocab([row["text"] for row in train_rows], max_words=20000)
    (OUTPUT / "vocab.json").write_text(json.dumps(vocab, indent=2), encoding="utf-8")
    ids, length = encode("The acting wasn't convincing, but I liked the music.", vocab, MAX_LENGTH)
    print("Vocabulary size:", len(vocab), "True length:", length)
    print("First token IDs:", ids[:12])
    print("English label mapping:", dict(enumerate(LABELS)))
    '''),md('''## 2. Define the model and training step

    Embedding maps IDs to vectors. A bidirectional LSTM summarizes the review in both
    directions. Concatenated final states feed a two-class linear layer. Sequence lengths
    are passed to the recurrent computation so padding does not contaminate final states.
    Gradient clipping limits unusually large updates.
    '''),code(TORCH_TEXT if framework=='pytorch' else PADDLE_TEXT),
    md('## 3. Train and select by validation accuracy'),code('''
    EPOCHS = 1 if SMOKE else 5
    checkpoint = OUTPUT / ("best_model.pt" if FRAMEWORK == "pytorch" else "best_model.pdparams")
    history, best_accuracy = [], -1.0
    for epoch in range(EPOCHS):
        train_loss, train_accuracy = run_epoch(train_loader, training=True)
        val_loss, val_accuracy = run_epoch(validation_loader)
        history.append([train_loss, val_loss, train_accuracy, val_accuracy])
        if val_accuracy > best_accuracy:
            best_accuracy = val_accuracy
            save_weights(checkpoint)
        print(f"Epoch {epoch + 1}/{EPOCHS} | training loss {train_loss:.4f} | "
              f"validation loss {val_loss:.4f} | validation accuracy {val_accuracy:.3f}")
    '''),md('## 4. Reload and evaluate on held-out test reviews'),code('''
    load_weights(checkpoint)
    test_loss, test_accuracy = run_epoch(test_loader)
    print(f"Test accuracy: {test_accuracy:.3f}; test loss: {test_loss:.4f}")
    metrics = {"test_accuracy": test_accuracy, "test_loss": test_loss,
               "best_validation_accuracy": best_accuracy, "seed": SEED,
               "smoke_test": SMOKE, "max_length": MAX_LENGTH, "labels": LABELS,
               "split_sizes": [len(train_rows), len(validation_rows), len(test_rows)]}
    (OUTPUT / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    import matplotlib.pyplot as plt
    values = np.asarray(history)
    fig, axis = plt.subplots(figsize=(7, 3))
    axis.plot(values[:, 2], label="Training")
    axis.plot(values[:, 3], label="Validation")
    axis.set(title="English sentiment classification", xlabel="Epoch", ylabel="Accuracy")
    axis.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT / "accuracy.png")
    plt.show()
    '''),md('## 5. Predict new English reviews'),code('''
    reviews = ["The movie was wonderful and the acting was excellent.",
               "The plot was boring and the ending was disappointing.",
               "I expected to hate it, but it was not bad at all."]
    probabilities = predict(reviews)
    for text, scores in zip(reviews, probabilities):
        label = int(np.argmax(scores))
        print(f"{LABELS[label]} ({scores[label]:.3f}): {text}")

    assert probabilities.shape == (len(reviews), 2)
    assert np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-5)
    # The same review should not change prediction because of other batch members.
    assert np.allclose(predict([reviews[0]])[0], probabilities[0], atol=1e-5)
    print("Predictions can be wrong, especially after a short classroom run.")
    '''),md('''## Exercises

    Compare a unidirectional and bidirectional model. Change the maximum length and
    measure truncation frequency. Inspect negation and mixed reviews. Keep all tuning
    on the validation set. To reproduce predictions later, restore the vocabulary,
    maximum length, architecture, class mapping, and weights together.

    For an already fine-tuned English transformer, use the optional pretrained-model
    lesson in the PyTorch route. Its SST-2 training task differs from this IMDb experiment;
    its published scores are not this course's results.
    ''')]
    notebook(f'03-sentiment-analysis/{framework}/notebooks/03-lstm-sentiment.ipynb',cells)


def main():
    existing = list(ROOT.glob('0*/**/*.ipynb'))
    if any(any(c.get('execution_count') is not None for c in json.loads(p.read_text(encoding='utf-8'))['cells']) for p in existing):
        raise RuntimeError('Executed notebooks already exist. Edit them in place to preserve saved outputs.')
    write('COURSE_ROOT','English deep-learning training course')
    cv_notebook('01-image-classification/notebooks/01-lenet-mnist.ipynb',
                'LeNet: handwritten digit classification','lenet-mnist')
    cv_notebook('01-image-classification/notebooks/02-lenet-cifar10.ipynb',
                'LeNet: CIFAR-10 image classification','lenet-cifar10',dataset='cifar10')
    cv_notebook('01-image-classification/notebooks/03-resnet-cifar10.ipynb',
                'ResNet18: transfer learning on CIFAR-10','resnet-cifar10',dataset='resnet')
    cv_notebook('01-image-classification/notebooks/extensions/04-lenet-custom-data.ipynb',
                'Custom digit classification with ImageFolder','custom-digits',custom=True)
    cv_notebook('01-image-classification/archive/01-lenet-mnist-copy1.ipynb',
                'LeNet MNIST: compact comparison edition','lenet-mnist-compact',compact=True)
    for framework in ('pytorch','paddle'):
        overview(framework)
        embeddings(framework)
        sentiment(framework)


if __name__=='__main__':
    main()
