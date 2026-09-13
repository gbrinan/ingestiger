"""Boundary regression tests with synthetic data; no client documents."""
import copy, importlib.util, json, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('pipeline',Path(__file__).resolve().parents[1]/'skills/ingestiger/scripts/pipeline.py')
pipeline=importlib.util.module_from_spec(spec);spec.loader.exec_module(pipeline)
class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.source=dict(source_id='S1',source_revision='v1',org_id='example',project_id='test',units=[dict(unit_id='u1',locator='Sheet1!D3',text='Draft only. Human sends the final order.')])
        self.request=pipeline.prepare(self.source,'test-model',100)['requests'][0]
        self.response=dict(request_id=self.request['request_id'],results=[dict(unit_id='u1',status='analyzed',needs=[dict(title='Draft',statement='Prepare draft',details=['Human sends final order'],departments=[],patterns=[],evidence=['Human sends the final order.'],claim_status='source_reported')])])
    def test_url_only_evidence_rejected(self):
        self.source['units'][0]['text']='https://example.org/item'
        req=pipeline.prepare(self.source,'test-model',100)['requests'][0]
        self.response['request_id']=req['request_id']
        self.response['results'][0]['needs'][0]['evidence']=['https://example.org/item']
        with self.assertRaisesRegex(ValueError,'URL alone'):pipeline.validate(req,self.response)
    def test_valid(self):pipeline.validate(self.request,self.response)
    def test_legacy_request_and_response_without_kind(self):
        self.request['prompt']='Previously recorded prompt with no kind field'
        self.request['request_id']=pipeline.digest({k:v for k,v in self.request.items() if k!='request_id'})
        self.response['request_id']=self.request['request_id']
        pipeline.validate(self.request,self.response)
        self.assertNotIn('kind',self.response['results'][0]['needs'][0])
    def test_unknown_fields_rejected_before_writing(self):
        for level in ('response','result','need'):
            for key in ('lifecycle','owner_scope','provenance','id','approval','typo'):
                with self.subTest(level=level,key=key),tempfile.TemporaryDirectory() as td:
                    response=copy.deepcopy(self.response)
                    target={'response':response,'result':response['results'][0],'need':response['results'][0]['needs'][0]}[level]
                    target[key]='current'
                    out=Path(td)/'candidate'
                    with self.assertRaises(ValueError):pipeline.build(self.request,response,out)
                    self.assertFalse(out.exists())
    def test_candidate_kind_and_writer_owned_metadata(self):
        for kind in pipeline.KINDS:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as td:
                self.response['results'][0]['needs'][0]['kind']=kind
                out=Path(td)/'candidate';pipeline.build(self.request,self.response,out)
                saved=json.loads((out/'C0001.json').read_text(encoding='utf-8'))
                self.assertEqual(saved['kind'],kind)
                self.assertEqual(saved['lifecycle'],'candidate')
                self.assertEqual(saved['owner_scope'],{'org_id':'example','project_id':'test'})
                self.assertEqual(saved['provenance'],{'source_id':'S1','source_revision':'v1','locator':'Sheet1!D3','evidence_kind':'EXTRACTED'})
    def test_invalid_kind_rejected(self):
        for kind in ('current','approved','',None,{},[]):
            with self.subTest(kind=kind):
                self.response['results'][0]['needs'][0]['kind']=kind
                with self.assertRaises(ValueError):pipeline.validate(self.request,self.response)
    def test_exact_quote_cannot_complete_semantic_review(self):
        self.response['results'][0]['needs'][0]['statement']='Automatically sends final order'
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'candidate';pipeline.build(self.request,self.response,out)
            validation=json.loads((out/'validation.json').read_text(encoding='utf-8'))
            self.assertTrue(validation['structural_pass'])
            self.assertEqual(validation['semantic_review'],'pending')
            self.assertFalse(validation['published'])
            before=(out/'C0001.json').read_bytes()
            with self.assertRaises(ValueError):pipeline.build(self.request,self.response,out)
            self.assertEqual((out/'C0001.json').read_bytes(),before)
    def test_bad_quote(self):
        self.response['results'][0]['needs'][0]['evidence']=['Auto-send approved']
        with self.assertRaises(ValueError):pipeline.validate(self.request,self.response)
    def test_missing_unit(self):
        self.response['results']=[]
        with self.assertRaises(ValueError):pipeline.validate(self.request,self.response)
    def test_duplicate_unit(self):
        self.response['results']*=2
        with self.assertRaises(ValueError):pipeline.validate(self.request,self.response)
    def test_approval(self):
        self.response['results'][0]['needs'][0]['claim_status']='approved'
        with self.assertRaises(ValueError):pipeline.validate(self.request,self.response)
    def test_tampered_request(self):
        self.request['org_id']='another-company'
        with self.assertRaises(ValueError):pipeline.validate(self.request,self.response)
    def test_changed_prompt_model_source_changes_key(self):
        other=pipeline.prepare(self.source,'other-model',100)['requests'][0]
        self.assertNotEqual(other['request_id'],self.request['request_id'])
        self.source['units'][0]['text']+=' Changed.'
        other=pipeline.prepare(self.source,'test-model',100)['requests'][0]
        self.assertNotEqual(other['request_id'],self.request['request_id'])
    def test_oversize_fails_without_silent_truncation(self):
        with self.assertRaises(ValueError):pipeline.prepare(self.source,'test-model',3)
if __name__=='__main__':unittest.main()
