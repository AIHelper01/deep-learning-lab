"""Run using the detection environment; no network or real dataset mutation."""
from pathlib import Path
import json
import sys
import tempfile
from PIL import Image
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'english/scripts'))
sys.path.insert(0,str(ROOT/'english/common'))
from fetch_rps import prepare_export
from detection_data import prepare_rps


def expect_error(error, call):
    try:call()
    except error:return
    raise AssertionError(f'Expected {error.__name__}')


def main():
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary);source=root/'source';source.mkdir()
        config={'names':['0','1','2'],'roboflow':{'workspace':'melikeavan',
                'project':'rock-paper-scissors-ishcs','version':1,'license':'CC BY 4.0'}}
        (source/'data.yaml').write_text(yaml.safe_dump(config),encoding='utf-8')
        for i,split in enumerate(('train','valid','test')):
            (source/split/'images').mkdir(parents=True);(source/split/'labels').mkdir()
            Image.new('RGB',(100,100),(i*60,60,90)).save(source/split/'images/a.jpg')
            (source/split/'labels/a.txt').write_text(f'{i} 0.5 0.5 0.4 0.4\n',encoding='utf-8')
        output=root/'output'
        expect_error(ValueError,lambda:prepare_export(source,output))
        assert not output.exists(),'Failed import published a dataset.'
        names,counts=prepare_export(source,output,['paper','rock','scissors'])
        assert names==['paper','rock','scissors']
        assert all(r=={'images':1,'boxes':1} for r in counts.values())
        assert yaml.safe_load((source/'data.yaml').read_text())['names']==['0','1','2'],'Source changed.'
        assert yaml.safe_load((output/'data.yaml').read_text())['train']=='train/images'
        expect_error(FileExistsError,lambda:prepare_export(source,output,['paper','rock','scissors']))
        config['names']=names;config['roboflow']['project']='wrong-source'
        (source/'data.yaml').write_text(yaml.safe_dump(config),encoding='utf-8')
        expect_error(ValueError,lambda:prepare_rps(source,root/'bad.yaml'))
        assert not (root/'bad.yaml').exists(),'Rejected source wrote a config.'
        config['roboflow']['project']='rock-paper-scissors-ishcs'
        (source/'data.yaml').write_text(yaml.safe_dump(config),encoding='utf-8')
        (source/'test/labels/a.txt').write_text('2 1.0 0.5 0.5 0.5\n')
        expect_error(ValueError,lambda:prepare_export(source,root/'bad-output'))
        assert not (root/'bad-output').exists(),'Invalid boxes published a dataset.'
    print('PASS: source gate, explicit mapping, stable IDs, original source preservation, split paths, overwrite guard, and invalid-box rejection.')


if __name__=='__main__':main()
