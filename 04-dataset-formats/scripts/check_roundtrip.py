"""Check all six box-format directions, then optionally convert the real test split."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import tempfile
from PIL import Image
from convert import load_dataset, save_dataset, check_box


def compare(expected_names, expected, actual_names, actual):
    assert actual_names == expected_names, 'Class order changed.'
    def key(row): return row['split'],row['relative'].as_posix()
    left={key(r):r for r in expected};right={key(r):r for r in actual}
    assert left.keys()==right.keys(),'Images or splits changed.'
    for k,a in left.items():
        b=right[k]
        assert hashlib.sha256(a['image'].read_bytes()).digest()==hashlib.sha256(b['image'].read_bytes()).digest(),'Image bytes changed.'
        assert (a['width'],a['height'])==(b['width'],b['height'])
        assert len(a['boxes'])==len(b['boxes']),'Box count changed.'
        for (ca,ba),(cb,bb) in zip(a['boxes'],b['boxes']):
            assert ca==cb,'Category changed.'
            assert max(abs(x-y) for x,y in zip(ba,bb))<0.001,'Coordinates changed.'


def fixture_check():
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary)
        image=root/'fixture.jpg';Image.new('RGB',(640,480),(80,120,160)).save(image)
        records=[{'image':image,'relative':Path('nested/example.jpg'),'split':'test',
                  'width':640,'height':480,'boxes':[(2,[0.0,0.0,640.0,480.0]),(0,[123.45,67.89,102.3,211.7])]},
                 {'image':image,'relative':Path('empty.jpg'),'split':'test',
                  'width':640,'height':480,'boxes':[]}]
        names=['paper','rock','scissors']
        for kind in ('yolo','voc','coco'): save_dataset(root/kind,kind,names,records)
        directions=[]
        for source,target in itertools.permutations(('yolo','voc','coco'),2):
            n,rows=load_dataset(root/source,source,'test')
            destination=root/f'{source}-to-{target}'
            save_dataset(destination,target,n,rows)
            nn,rr=load_dataset(destination,target,'test')
            compare(names,records,nn,rr);directions.append(f'{source}->{target}')
        try: save_dataset(root/'yolo','yolo',names,records)
        except FileExistsError: pass
        else: raise AssertionError('Existing output was overwritten.')
        for box in ([0,0,0,2],[-2,0,3,3],[0,0,float('nan'),3],[639,0,2,3]):
            try:check_box(box,640,480)
            except ValueError:pass
            else:raise AssertionError('Invalid box was accepted.')
        return {'directions':directions,'image_count':2,'includes_empty_image':True,
                'includes_full_image_box':True,'includes_nested_path':True,
                'coordinate_tolerance_pixels':0.001,'overwrite_and_invalid_box_guards':'passed'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path)
    parser.add_argument('--output-root',type=Path,default=Path(__file__).resolve().parents[1]/'data')
    args=parser.parse_args()
    report={'fixture':fixture_check(),'status':'passed'}
    if args.source:
        names,records=load_dataset(args.source,'yolo','test')
        real={'images':len(records),'boxes':sum(len(r['boxes']) for r in records),'checks':[]}
        for kind in ('voc','coco'):
            destination=args.output_root/f'rps-{kind}-test'
            save_dataset(destination,kind,names,records)
            n,rows=load_dataset(destination,kind,'test');compare(names,records,n,rows)
            back=args.output_root/f'rps-yolo-from-{kind}'
            save_dataset(back,'yolo',n,rows)
            nn,rr=load_dataset(back,'yolo','test');compare(names,records,nn,rr)
            real['checks'].append(f'yolo->{kind}->yolo')
        report['real_test_split']=real
        folder=Path(__file__).resolve().parents[1]/'reports';folder.mkdir(exist_ok=True)
        (folder/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
