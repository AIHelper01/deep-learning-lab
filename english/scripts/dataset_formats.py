"""Convert bounding-box detection datasets between YOLO, VOC, and COCO.

Uses Pillow and PyYAML from the course detection environment. No segmentation,
keypoints, rotated boxes, or crowd-region approximation is performed.
"""
from pathlib import Path
import argparse
import json
import math
import shutil
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

from PIL import Image
import yaml

FORMATS = ('yolo', 'voc', 'coco')


def image_paths(folder):
    return sorted(p for p in folder.rglob('*') if p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'})


def check_box(box, width, height):
    x, y, w, h = box
    if not all(math.isfinite(v) for v in box) or min(w, h) <= 0:
        raise ValueError(f'Non-finite or degenerate box: {box}')
    # Tolerance covers decimal serialization, not invalid source annotations.
    if min(x, y) < -0.001 or x+w > width+0.001 or y+h > height+0.001:
        raise ValueError(f'Box outside image: {box}, image={width}x{height}')


def load_dataset(source, kind, split='all'):
    source = Path(source)
    if kind == 'yolo':
        config = yaml.safe_load((source/'data.yaml').read_text(encoding='utf-8'))
        names = config['names']
        if isinstance(names, dict):
            names = {int(k): v for k,v in names.items()}
            if sorted(names) != list(range(len(names))):
                raise ValueError('YOLO class IDs must be consecutive from zero.')
            names = [names[i] for i in range(len(names))]
        names = [str(n) for n in names]
    else:
        names = json.loads((source/'classes.json').read_text(encoding='utf-8'))
    if not names or len(set(names)) != len(names):
        raise ValueError('Class names must be nonempty and unique.')
    records = []
    splits = ('train','valid','test') if split == 'all' else (split,)
    for part in splits:
        folder = source/part
        if not folder.exists():
            if split != 'all': raise FileNotFoundError(folder)
            continue
        annotations = defaultdict(list)
        if kind == 'coco':
            coco = json.loads((source/'annotations'/f'instances_{part}.json').read_text(encoding='utf-8'))
            categories = {c['id']: names.index(c['name']) for c in coco['categories']}
            by_id = {r['id']:r for r in coco['images']}
            if len(by_id) != len(coco['images']): raise ValueError('Duplicate COCO image IDs.')
            for a in coco['annotations']:
                if a.get('iscrowd',0) or a.get('segmentation'):
                    raise ValueError('Only plain bounding boxes are supported; masks/crowds require a separate workflow.')
                if a['image_id'] not in by_id: raise ValueError('Unknown COCO image ID.')
                annotations[a['image_id']].append((categories[a['category_id']],list(map(float,a['bbox']))))
            source_images = []
            for r in coco['images']:
                relative = Path(r['file_name'])
                image = (folder/'images'/relative).resolve()
                if not image.is_relative_to((folder/'images').resolve()): raise ValueError('Unsafe COCO filename.')
                source_images.append((image,relative,annotations[r['id']],(r['width'],r['height'])))
        else:
            image_root = folder/('JPEGImages' if kind == 'voc' else 'images')
            source_images = [(p,p.relative_to(image_root),None,None) for p in image_paths(image_root)]
        for image,relative,boxes,declared in source_images:
            with Image.open(image) as im: width,height = im.size
            if declared and declared != (width,height): raise ValueError('COCO image dimensions disagree with file.')
            if boxes is None:
                boxes=[]
                if kind == 'yolo':
                    label=folder/'labels'/relative.with_suffix('.txt')
                    for line in label.read_text(encoding='utf-8').splitlines():
                        if not line.strip(): continue
                        fields=line.split()
                        if len(fields)!=5: raise ValueError('Expected five YOLO detection fields.')
                        category=int(fields[0]);xc,yc,w,h=map(float,fields[1:])
                        boxes.append((category,[(xc-w/2)*width,(yc-h/2)*height,w*width,h*height]))
                else:
                    node=ET.parse(folder/'Annotations'/relative.with_suffix('.xml')).getroot()
                    if (int(node.findtext('size/width')),int(node.findtext('size/height'))) != (width,height):
                        raise ValueError('VOC image dimensions disagree with file.')
                    if node.findtext('coordinate_convention') != 'zero-based-continuous-xyxy':
                        raise ValueError('VOC coordinate convention must be declared by this tutorial exporter. '
                                         'Adapt 1-based inclusive datasets explicitly before importing.')
                    for obj in node.findall('object'):
                        if obj.findtext('difficult','0') != '0': raise ValueError('VOC difficult flag requires explicit handling.')
                        x1,y1,x2,y2=[float(obj.findtext('bndbox/'+k)) for k in ('xmin','ymin','xmax','ymax')]
                        boxes.append((names.index(obj.findtext('name')),[x1,y1,x2-x1,y2-y1]))
            for category,box in boxes:
                if category not in range(len(names)): raise ValueError('Unknown class ID.')
                check_box(box,width,height)
            records.append({'image':image,'relative':relative,'split':part,'width':width,'height':height,'boxes':boxes})
    if not records: raise ValueError('No images found in supported train/valid/test layout.')
    return names,records


def save_dataset(destination, kind, names, records):
    destination=Path(destination)
    if destination.exists(): raise FileExistsError(f'Refusing to overwrite {destination}')
    destination.parent.mkdir(parents=True,exist_ok=True)
    counts=Counter();boxes_count=Counter()
    with tempfile.TemporaryDirectory(prefix='format-conversion-',dir=destination.parent) as temporary:
        output=Path(temporary)/'dataset';output.mkdir()
        (output/'classes.json').write_text(json.dumps(names,indent=2)+'\n',encoding='utf-8')
        (output/'classes.txt').write_text('\n'.join(names)+'\n',encoding='utf-8')
        coco={}
        for row in records:
            part=row['split'];relative=row['relative'];width,height=row['width'],row['height']
            folder=output/part
            target=folder/('JPEGImages' if kind=='voc' else 'images')/relative
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(row['image'],target)
            counts[part]+=1;boxes_count[part]+=len(row['boxes'])
            if kind=='yolo':
                label=folder/'labels'/relative.with_suffix('.txt');label.parent.mkdir(parents=True,exist_ok=True)
                rows=[]
                for category,(x,y,w,h) in row['boxes']:
                    rows.append(f'{category} {(x+w/2)/width:.10f} {(y+h/2)/height:.10f} {w/width:.10f} {h/height:.10f}')
                label.write_text('\n'.join(rows)+('\n' if rows else ''),encoding='utf-8')
            elif kind=='voc':
                node=ET.Element('annotation');ET.SubElement(node,'filename').text=relative.as_posix()
                ET.SubElement(node,'coordinate_convention').text='zero-based-continuous-xyxy'
                size=ET.SubElement(node,'size')
                for key,value in [('width',width),('height',height),('depth',3)]: ET.SubElement(size,key).text=str(value)
                for category,(x,y,w,h) in row['boxes']:
                    obj=ET.SubElement(node,'object');ET.SubElement(obj,'name').text=names[category]
                    ET.SubElement(obj,'difficult').text='0';box=ET.SubElement(obj,'bndbox')
                    for key,value in zip(('xmin','ymin','xmax','ymax'),(x,y,x+w,y+h)): ET.SubElement(box,key).text=f'{value:.8f}'
                label=folder/'Annotations'/relative.with_suffix('.xml');label.parent.mkdir(parents=True,exist_ok=True)
                ET.indent(node);ET.ElementTree(node).write(label,encoding='utf-8',xml_declaration=True)
            else:
                doc=coco.setdefault(part,{'images':[],'annotations':[],
                    'categories':[{'id':i+1,'name':name} for i,name in enumerate(names)]})
                image_id=len(doc['images'])+1
                doc['images'].append({'id':image_id,'file_name':relative.as_posix(),'width':width,'height':height})
                for category,(x,y,w,h) in row['boxes']:
                    doc['annotations'].append({'id':len(doc['annotations'])+1,'image_id':image_id,
                        'category_id':category+1,'bbox':[x,y,w,h],'area':w*h,'iscrowd':0})
        if kind=='yolo':
            config={'names':names,'nc':len(names)}
            for part in counts: config['val' if part=='valid' else part]=f'{part}/images'
            (output/'data.yaml').write_text(yaml.safe_dump(config,sort_keys=False),encoding='utf-8')
        for part,doc in coco.items():
            directory=output/'annotations';directory.mkdir(exist_ok=True)
            (directory/f'instances_{part}.json').write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8')
        report={'format':kind,'class_order':names,'images':dict(counts),'boxes':dict(boxes_count),
                'scope':'Axis-aligned detection boxes only; no resplitting, clipping, filtering, or augmentation.'}
        (output/'conversion.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        output.rename(destination)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--input-format',choices=FORMATS,required=True)
    parser.add_argument('--output-format',choices=FORMATS,required=True)
    parser.add_argument('--destination',type=Path,required=True)
    parser.add_argument('--split',choices=['all','train','valid','test'],default='all')
    args=parser.parse_args()
    names,records=load_dataset(args.source,args.input_format,args.split)
    print(json.dumps(save_dataset(args.destination,args.output_format,names,records),indent=2))


if __name__=='__main__': main()
