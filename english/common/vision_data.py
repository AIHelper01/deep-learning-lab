"""CIFAR-10 with a pinned university-published Parquet mirror fallback."""
from pathlib import Path
import hashlib
import io
import json
import requests
from PIL import Image
from torch.utils.data import Dataset
from torchvision.datasets import CIFAR10

REVISION = '0b2714987fa478483af9968de7c934580d0bb9a2'
HASHES = {'train': '8428b53a88a11ac374111006708df51469e315a22ac6d66470afd9c78d2ae883',
          'test': '841389e6f2d64f28bf17310e430aebac20ec3ba611a3c5e231dc93c645ce84de'}
CLASSES = ['airplane','automobile','bird','cat','deer','dog','frog','horse','ship','truck']


class ParquetCIFAR10(Dataset):
    def __init__(self, path, transform=None):
        import pyarrow.parquet as pq
        self.table = pq.read_table(path, columns=['img','label'])
        self.transform = transform
        self.classes = CLASSES
        self.targets = self.table['label'].to_pylist()
        if set(self.targets) != set(range(10)):
            raise ValueError('CIFAR-10 must have exactly ten numeric class IDs.')

    def __len__(self):
        return self.table.num_rows

    def __getitem__(self, index):
        record = self.table['img'][int(index)].as_py()
        image = Image.open(io.BytesIO(record['bytes'])).convert('RGB')
        if image.size != (32,32):
            raise ValueError('Unexpected CIFAR-10 image size.')
        if self.transform is not None:
            image = self.transform(image)
        return image, self.targets[int(index)]


def load_cifar10(root, train=True, transform=None):
    root = Path(root)
    # Reuse a complete, checksum-verified torchvision download when available.
    try:
        return CIFAR10(root, train=train, transform=transform, download=False)
    except RuntimeError:
        pass
    split = 'train' if train else 'test'
    root.mkdir(parents=True, exist_ok=True)
    name = f'{split}-00000-of-00001.parquet'
    path = root/name
    url = f'https://huggingface.co/datasets/uoft-cs/cifar10/resolve/{REVISION}/plain_text/{name}'
    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != HASHES[split]:
        print(f'Downloading CIFAR-10 {split} from the university-published mirror.')
        temporary = path.with_suffix('.part')
        with requests.get(url, stream=True, timeout=90) as response, temporary.open('wb') as handle:
            response.raise_for_status()
            for chunk in response.iter_content(1024*1024):
                if chunk:
                    handle.write(chunk)
        if hashlib.sha256(temporary.read_bytes()).hexdigest() != HASHES[split]:
            raise ValueError('CIFAR-10 mirror checksum mismatch.')
        temporary.replace(path)
    dataset = ParquetCIFAR10(path, transform)
    expected = 50000 if train else 10000
    if len(dataset) != expected:
        raise ValueError(f'Expected {expected} CIFAR-10 examples in this split.')
    (root/f'{split}-provenance.json').write_text(json.dumps({
        'source':url,'revision':REVISION,'sha256':HASHES[split],
        'split':split,'count':len(dataset),'classes':CLASSES},indent=2)+'\n',encoding='utf-8')
    return dataset
