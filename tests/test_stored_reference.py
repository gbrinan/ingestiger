import importlib.util,json,tempfile,unittest,hashlib
from pathlib import Path
base=Path(__file__).resolve().parents[1]/'skills/ingestiger/scripts'
def module(name):
    s=importlib.util.spec_from_file_location(name,base/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
g=module('golden');p=module('pipeline')
class StoredReferenceTests(unittest.TestCase):
    def test_channel_requires_explicit_input_and_legacy_retry_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);image=root/'image.jpg';raw=b'\xff\xd8\xffstored-only-fixture';image.write_bytes(raw)
            folder=g.register(image,root/'golden','GS1','org','project','user-selected')
            self.assertEqual(g.load(folder/'sample.json')['channel'],'unknown')
            self.assertEqual((folder/'original.jpg').read_bytes(),raw)
            # Existing records can carry the old channel; re-registration must not migrate them.
            existing=g.load(folder/'sample.json');existing['channel']='sns-ad';g.write(folder/'sample.json',existing)
            before=(folder/'sample.json').read_bytes()
            self.assertEqual(g.register(image,root/'golden','GS1','org','project','user-selected'),folder)
            self.assertEqual((folder/'sample.json').read_bytes(),before)
            with self.assertRaises(ValueError):g.register(image,root/'golden','GS1','org','project','user-selected','training')
            self.assertEqual((folder/'sample.json').read_bytes(),before)
            explicit=g.register(image,root/'golden','GS2','org','project','user-selected','training')
            self.assertEqual(g.load(explicit/'sample.json')['channel'],'training')
    def test_blank_channel_rejected_before_storage(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'Invalid channel'):
                g.register(Path(td)/'unread.jpg',Path(td)/'golden','GS1','org','project','selected',' ')
            self.assertFalse((Path(td)/'golden').exists())
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
