"""Isolated skill copy, Korean paths and strict encoding warnings; no Windows claim."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


class Utf8CliTests(unittest.TestCase):
    def test_all_runtime_clis_with_korean_paths(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'한글 작업공간';root.mkdir()
            skill=root/'skill'
            shutil.copytree(Path(__file__).resolve().parents[1]/'skills/ingestiger',skill,
                            ignore=shutil.ignore_patterns('__pycache__'))
            def run(script,*args):
                return subprocess.run([sys.executable,'-X','warn_default_encoding','-W','error::EncodingWarning',
                    str(skill/'scripts'/script),*map(str,args)],cwd=root,check=True,
                    capture_output=True,encoding='utf-8')
            def dump(name,data):
                path=root/name;path.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8');return path
            def load(name):return json.loads((root/name).read_text(encoding='utf-8'))
            source=dump('입력.json',dict(source_id='S1',source_revision='v1',org_id='org',project_id='project',
                units=[dict(unit_id='u1',locator='자료!A1',text='최종 발송은 사람이 한다.')]))
            before=source.read_bytes()
            run('pipeline.py','prepare',source,'요청들.json','--model','synthetic')
            request=load('요청들.json')['requests'][0];dump('요청.json',request)
            dump('응답.json',dict(request_id=request['request_id'],results=[dict(unit_id='u1',status='analyzed',needs=[
                dict(kind='constraint',title='발송 조건',statement='사람이 최종 발송한다.',details=[],departments=[],patterns=[],
                     evidence=['최종 발송은 사람이 한다.'],claim_status='source_reported')])]))
            run('pipeline.py','build','요청.json','응답.json','후보')
            self.assertEqual(load('후보/C0001.json')['title'],'발송 조건')
            self.assertIn('정본 승격 전 후보',(root/'후보/index.md').read_text(encoding='utf-8'))
            self.assertEqual(source.read_bytes(),before)
            dump('시트.json',{'spreadsheet_id':'fixture','sheets':[{'title':'자료','cells':[
                {'cell':'A1','value':{'stringValue':'한글 요구'}}]}]})
            run('link_audit.py','시트.json','감사.json')
            self.assertEqual(load('감사.json')['units'][0]['text'],'한글 요구')
            raw=b'\xff\xd8\xffstored-only-fixture';(root/'샘플.jpg').write_bytes(raw)
            run('golden.py','register','샘플.jpg','이미지','--id','GS1','--org','org','--project','project','--selection-quote','사용자 선정')
            run('golden.py','render','이미지/GS1')
            run('golden.py','packet','이미지/GS1','포인터.json','--org','org','--project','project')
            self.assertEqual(load('포인터.json')['selection']['evidence'],'사용자 선정')
            self.assertEqual((root/'이미지/GS1/original.jpg').read_bytes(),raw)
            with zipfile.ZipFile(root/'발표.key','w') as z:z.writestr('Index/Slide-1.iwa',b'synthetic')
            run('deck_inventory.py','발표.key','발표목록.json')
            self.assertTrue(load('발표목록.json'))


if __name__=='__main__':unittest.main()
