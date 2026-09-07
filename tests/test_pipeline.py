"""Boundary regression tests with synthetic data; no client documents."""
import copy, importlib.util, unittest
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
