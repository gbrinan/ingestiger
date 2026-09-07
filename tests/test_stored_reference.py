import importlib.util,json,tempfile,unittest,hashlib
from pathlib import Path
base=Path(__file__).resolve().parents[1]/'skills/ingestiger/scripts'
def module(name):
    s=importlib.util.spec_from_file_location(name,base/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
g=module('golden');p=module('pipeline')
class StoredReferenceTests(unittest.TestCase):
    def test_pointer_does_not_require_visual_review(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);image=root/'image.jpg';image.write_bytes(b'\xff\xd8\xffstored-only-fixture')
            folder=g.register(image,root/'golden','GS1','org','project','user-selected')
            pointer=g.packet(folder,'org','project')
            self.assertNotIn('observation',pointer);self.assertNotIn('criteria',pointer)
            source=dict(source_id='S1',source_revision='v1',org_id='org',project_id='project',units=[dict(unit_id='u1',locator='p1',text='Need')],reference_samples=[pointer])
            req=p.prepare(source,'test',100)['requests'][0]
            p.validate(req,{'request_id':req['request_id'],'results':[{'unit_id':'u1','status':'analyzed','needs':[]}]})
            pointer['criteria']=[]
            with self.assertRaises(ValueError):p.prepare(source,'test',100)
if __name__=='__main__':unittest.main()
